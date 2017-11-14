import sys
import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
from PhysicsTools.PatAlgos.tools.tauTools import *
from RecoMET.METPUSubtraction.MVAMETConfiguration_cff import runMVAMET

options = VarParsing ('python')
options.register ('globalTag',"80X_mcRun2_asymptotic_2016_miniAODv2_v1",VarParsing.multiplicity.singleton,VarParsing.varType.string,'input global tag to be used');
options.register ('inputFile', 'file:/afs/cern.ch/work/m/mverzett/public/perRic/t3mMINIAODSIM/t3mu_MINIAODSIM_0.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Path to a testfile")
# options.register ('inputFile', 'file:////storage/jbod/nzaeh/00E9D1DA-105D-E611-A56E-FA163EE988CA.root', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Path to a testfile")
options.register ("localSqlite", '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "Path to a local sqlite file")
options.register ("reapplyJEC", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Reapply JEC to Jets")
options.register ("reapplyPUJetID", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Reapply PU Jet ID")
options.register ("recomputeMET", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Recomute MET instead of taking it from MiniAOD")
options.register ("isData", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "Input is data")
options.parseArguments()

process = cms.Process("MVAMET")

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
jetCollection = "slimmedJets"

if (options.localSqlite == ''):
    process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
    process.GlobalTag.globaltag = options.globalTag
else:
    from RecoMET.METPUSubtraction.jet_recorrections import loadLocalSqlite
    loadLocalSqlite(process, options.localSqlite) 

if options.reapplyPUJetID:
    from RecoMET.METPUSubtraction.jet_recorrections import reapplyPUJetID
    reapplyPUJetID(process)

if options.reapplyJEC:
    from RecoMET.METPUSubtraction.jet_recorrections import recorrectJets
    recorrectJets(process, options.isData)
    jetCollection = "patJetsReapplyJEC"

if options.recomputeMET:
	from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
	runMetCorAndUncFromMiniAOD(process, isData=options.isData, jetCollUnskimmed=jetCollection  )

	from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
	makePuppiesFromMiniAOD( process );
	runMetCorAndUncFromMiniAOD(process,
                             isData=options.isData,
                             metType="Puppi",
                             pfCandColl=cms.InputTag("puppiForMET"),
                             recoMetFromPFCs=True,
                             reclusterJets=True,
                             jetFlavor="AK4PFPuppi",
                             postfix="Puppi")


if options.reapplyPUJetID:
    getattr(process, jetCollection).userData.userFloats.src += ['pileupJetIdUpdated:fullDiscriminant']

# configure MVA MET
runMVAMET( process, jetCollectionPF = jetCollection, debug=True)

## set input files
process.source = cms.Source("PoolSource")
process.source.fileNames = cms.untracked.vstring(options.inputFile)
## logger
process.load('FWCore.MessageLogger.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 50

#! Output and Log                                                                                                                                                            
process.options   = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))
#  in >= 910 this is irrelevant https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideUnscheduledExecution
# process.options.allowUnscheduled = cms.untracked.bool(True)
# process.options.allowUnscheduled = cms.untracked.bool(False)


##########################################################################################
# configure the unscheduled mode appropriately in >= 910
# combine all this info
# https://hypernews.cern.ch/HyperNews/CMS/get/edmFramework/3787.html
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideAboutPythonConfigFile#Task_Objects
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideUnscheduledExecution
# dump the full cfg in 8026
process.MVAMETtask = cms.Task(
    process.egmGsfElectronIDTask,
    process.slimmedMuonsTight,
    process.slimmedElectronsTight,
    process.slimmedTausLoose,
    process.slimmedTausLooseCleaned,
    process.tausSignificance,
    process.tauMET,
    process.tauPFMET,
    process.allDecayProducts,
    process.tauDecayProducts,
    process.patpfTrackMET,
    process.pfTrackMET,
    process.pfTrackMETCands,
    process.pfChargedPV,
    process.patpfNoPUMET,
    process.pfNoPUMET,
    process.pfNoPUMETCands,
    process.neutralInJets,
    process.patJetsReapplyJEC,
    process.patJetCorrFactorsReapplyJEC,
    process.pileupJetIdUpdated,
    process.pfNeutrals,
    process.patpfPUCorrectedMET,
    process.pfPUCorrectedMET,
    process.pfPUCorrectedMETCands,
    process.patpfPUMET,
    process.pfPUMET,
    process.pfPUMETCands,
    process.pfChargedPU,
    process.MVAMET
)

process.p = cms.Path(
    process.MVAMETtask
)
##########################################################################################

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
) 


process.output = cms.OutputModule("PoolOutputModule",
                                  fileName = cms.untracked.string('output.root'),
                                  outputCommands = cms.untracked.vstring(
                                                                         'keep patMETs_slimmedMETs_*_MVAMET',
                                                                         'keep patMETs_slimmedMETsPuppi_*_MVAMET',
                                                                         'keep patMETs_MVAMET_*_MVAMET',
                                                                         'keep *_patJetsReapplyJEC_*_MVAMET',
                                                                         'keep *',
                                                                         ),        
                                  SelectEvents = cms.untracked.PSet(  SelectEvents = cms.vstring('p'))
 
                                 )

process.out = cms.EndPath(process.output)
