import FWCore.ParameterSet.Config as cms
import sys


import FWCore.ParameterSet.Config as cms
import sys

from RecoMET.METPUSubtraction.LeptonSelectionTools_cff import applyMuonID
from RecoMET.METPUSubtraction.LeptonSelectionTools_cff import applyElectronID
from RecoMET.METPUSubtraction.LeptonSelectionTools_cff import applyTauID
#from RecoMET.METPUSubtraction.LeptonSelectionTools_cff import cleanJetsFromLeptons
from RecoMET.METProducers.PFMET_cfi import pfMet
from PhysicsTools.SelectorUtils.tools.vid_id_tools import switchOnVIDElectronIdProducer, switchOnVIDPhotonIdProducer, DataFormat, setupAllVIDIdsInModule, setupVIDElectronSelection, setupVIDPhotonSelection

def runMVAMET(process,
                 srcMuons =  "slimmedMuons", ## inputMuonCollection
                 muonTypeID    = "Tight", ## type of muon ID to be applied                                                                                                   
                 typeIsoMuons  = "dBeta", ## isolation type to be used for muons                                                                                               
                 relativeIsoCutMuons = 0.12,
                 srcElectrons = "slimmedElectrons", 
                 electronTypeID= "Tight", 
                 electronID_map = 'egmGsfElectronIDs:cutBasedElectronID-Spring15-25ns-V1-standalone-tight',
                 typeIsoElectrons = "rhoCorr",
                 relativeIsoCutEletrons = 0.12,
                 srcTaus = "slimmedTaus",
                 tauTypeID = "Loose",
                 jetCollectionPF    = "slimmedJets",
                 dRCleaning= 0.3, 
                 jetPtCut = 15, 
                 jetEtaCut =5.,
                 saveMapForTraining = False,
                 debug = False
                 ):

    
    if not hasattr(process,"egmGsfElectronIDs"):
        electronIdModules = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff']
    
        switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
    
        for idMod in electronIdModules:
            setupAllVIDIdsInModule(process, idMod, setupVIDElectronSelection)
    """
    if not hasattr(process,"VersionedPhotonIdProducer"):
        switchOnVIDPhotonIdProducer(process, DataFormat.MiniAOD)
    
        photonIdModules = ['RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_PHYS14_PU20bx25_V2_cff']
    
        for idMod in photonIdModules:
            setupAllVIDIdsInModule(process, idMod, setupVIDPhotonSelection)
    """
     ## create the Path
    process.jmfw_analyzers = cms.Sequence()
    if( not hasattr(process, "p")):
        process.p = cms.Path()
    process.p += process.jmfw_analyzers
    # additional contribution from hadronically decaying taus
    from RecoMET.METPUSubtraction.tausSignificance import tausSignificance, tauMET, tauPFMET, tauDecayProducts, allDecayProducts
    process.tausSignificance = tausSignificance
    process.tauMET = tauMET
    process.tauMET.srcPFCands =  cms.InputTag("packedPFCandidates")
    process.tauPFMET = tauPFMET
    process.tauDecayProducts = tauDecayProducts
    process.allDecayProducts = allDecayProducts
   
    relativeIsoCutMuonsLoose = relativeIsoCutMuons+0.05;
    relativeIsoCutEletronsLoose = relativeIsoCutEletrons+0.05;    

    ### run Muon ID
    applyMuonID(process, 
                src   = srcMuons,
                label = muonTypeID, 
                iso_map_charged_hadron  = '',
                iso_map_neutral_hadron  = '',
                iso_map_photon          = '',
                typeIso                 = typeIsoMuons,
                relativeIsolationCutVal = relativeIsoCutMuons
                )


    ### run Electron ID
    applyElectronID(process, 
                    label = electronTypeID, 
                    src   = srcElectrons,
                    iso_map_charged_hadron  = '',
                    iso_map_neutral_hadron  = '',
                    iso_map_photon          = '',
                    typeIso = typeIsoElectrons,
                    electron_id_map = electronID_map,
                    relativeIsolationCutVal = relativeIsoCutEletrons
                    )

    ### run tau ID                                        
    applyTauID( process, 
                label = tauTypeID, 
                src = srcTaus,
                muonCollection     = srcMuons+muonTypeID,
                electronCollection = srcElectrons+electronTypeID)

    ## jet lepton cleaning
    """
    cleanJetsFromLeptons(process,
                         label = "Cleaned",
                         jetCollection      = jetCollectionPF,
                         muonCollection     = srcMuons+muonTypeID,
                         electronCollection = srcElectrons+electronTypeID,
                         tauCollection      = srcTaus+tauTypeID+"Cleaned",
                         jetPtCut   = jetPtCut,
                         jetEtaCut  = jetEtaCut,
                         dRCleaning = dRCleaning)
    """

    #### Input definitions like in classic MVA MET
    #### tracks from PV
    process.pfCHS = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('fromPV'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    process.pfChargedPV = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('fromPV && charge !=0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    #### tracks not from PV
    process.pfChargedPU = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('!fromPV && charge !=0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    process.pfNeutrals  = cms.EDFilter("CandPtrSelector",
                                       cut = cms.string('charge ==0'),
                                       src = cms.InputTag("packedPFCandidates")
                                       )
    #### Neutrals in Jets passing PU Jet ID
    #### and Neutrals in Jets not passing PU Jet ID
    process.neutralInJets = cms.EDProducer("neutralCandidatePUIDJets",
                                           srcJets = cms.InputTag(jetCollectionPF),
                                           srcCandidates = cms.InputTag("pfNeutrals"),
                                           neutralParticlesPVJetsLabel = cms.string("neutralPassingPUIDJets"),
                                           neutralParticlesPUJetsLabel = cms.string("neutralFailingPUIDJets"),
                                           neutralParticlesUnclusteredLabel = cms.string("neutralParticlesUnclustered"),
                                           jetPUDIWP = cms.string("user"),
                                           jetPUIDMapLabel = cms.string("fullDiscriminant"))
  

    #### Merge collections to produce corresponding METs
    """
    process.pfMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(          
                                                                                          cms.InputTag("pfChargedPV"),
                                                                                          cms.InputTag("pfChargedPU"),
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralFailingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralParticlesUnclustered")
    ))
    """
    #### Track MET
    process.pfTrackMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("pfChargedPV")))
    ## No-PU MET
    process.pfNoPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(        cms.InputTag("pfChargedPV"),
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets")))
    ## PU corrected MET
    process.pfPUCorrectedMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag( cms.InputTag("pfChargedPV"), 
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralParticlesUnclustered")))
    ## PU MET
    process.pfPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(          cms.InputTag("pfChargedPU"),
                                                                                          cms.InputTag("neutralInJets", "neutralFailingPUIDJets")))
    
    ##Experimental
    process.pfChargedPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("pfChargedPU")))
    process.pfNeutralPUMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("neutralInJets", "neutralFailingPUIDJets")))
    process.pfNeutralPVMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("neutralInJets", "neutralPassingPUIDJets")))
    process.pfNeutralUnclusteredMETCands = cms.EDProducer("CandViewMerger", src = cms.VInputTag(cms.InputTag("neutralInJets", "neutralParticlesUnclustered")))

                                                          
    from PhysicsTools.PatAlgos.producersLayer1.metProducer_cfi import patMETs
    patMETsForMVA = patMETs.clone()
    patMETsForMVA.computeMETSignificance = cms.bool(False)
    patMETsForMVA.addGenMET = cms.bool(False)
    patMETsForMVA.srcJets = cms.InputTag(jetCollectionPF)

    setattr(patMETsForMVA,"srcLeptons", cms.VInputTag(srcMuons+muonTypeID,srcElectrons+electronTypeID,srcTaus+tauTypeID+"Cleaned"))

    """
    # get jets for T1 Correction
    from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
    from JetMETCorrections.Configuration.JetCorrectors_cff import ak4PFCHSL1FastL2L3Corrector,ak4PFCHSL3AbsoluteCorrector,ak4PFCHSL2RelativeCorrector,ak4PFCHSL1FastjetCorrector, ak4PFCHSL1FastL2L3ResidualCorrector, ak4PFCHSResidualCorrector
    process.ak4PFCHSL1FastL2L3Corrector = ak4PFCHSL1FastL2L3Corrector
    process.ak4PFCHSL1FastL2L3ResidualCorrector = ak4PFCHSL1FastL2L3ResidualCorrector
    process.ak4PFCHSResidualCorrector = ak4PFCHSResidualCorrector
    process.ak4PFCHSL3AbsoluteCorrector = ak4PFCHSL3AbsoluteCorrector
    process.ak4PFCHSL2RelativeCorrector = ak4PFCHSL2RelativeCorrector
    process.ak4PFCHSL1FastjetCorrector = ak4PFCHSL1FastjetCorrector 
    """

    for met in ["pfTrackMET", "pfNoPUMET", "pfPUCorrectedMET", "pfPUMET"]:
        # create PF METs
        setattr(process, met, pfMet.clone(src = cms.InputTag(met+"Cands"), alias = cms.string(met)))
        # convert METs to pat objects
        setattr(process, "pat"+met,      patMETsForMVA.clone(metSource = cms.InputTag(met)))

    process.pfChs = cms.EDProducer("CandViewMerger", src = cms.VInputTag(          
                                                                                          cms.InputTag("pfChargedPV"),
                                                                                          cms.InputTag("neutralInJets", "neutralPassingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralFailingPUIDJets"),
                                                                                          cms.InputTag("neutralInJets", "neutralParticlesUnclustered")
    ))

    ### MVA MET
    process.MVAMET = cms.EDProducer("MVAMET",                                                
                                    debug = cms.bool(debug),
                                    requireOS = cms.bool(True),
                                    combineNLeptons = cms.int32(2),
                                    MVAMETLabel = cms.string("MVAMET"),
                                    srcMETs      = cms.VInputTag(
                                                                 cms.InputTag("slimmedMETs"),
                                                                 cms.InputTag("patpfTrackMET"),
                                                                 cms.InputTag("patpfNoPUMET"),
                                                                 cms.InputTag("patpfPUCorrectedMET"),
                                                                 cms.InputTag("patpfPUMET"),
                                                                 cms.InputTag("slimmedMETsPuppi"),
                                                                ),
                                    inputMETFlags = cms.vint32(0,1,0,0,3,0),
                                    srcJets        = cms.InputTag(jetCollectionPF),
                                    srcVertices    = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                    srcTaus        = cms.InputTag(srcTaus+tauTypeID+"Cleaned"),
                                    srcMuons       = cms.InputTag(srcMuons+muonTypeID),
                                    srcElectrons       = cms.InputTag(srcElectrons+electronTypeID),
                                    weightFile     = cms.FileInPath('RecoMET/METPUSubtraction/data/weightfile.root'),
                                    #srcLeptons  = cms.VInputTag("slimmedMuons", "slimmedElectrons", "slimmedTaus"), # to produce all possible combinations
                                    srcLeptons  = cms.VInputTag(srcMuons+muonTypeID,srcElectrons+electronTypeID,srcTaus+tauTypeID+"Cleaned"), # to produce a selection specifically designed for trainings
                                    useTauSig = cms.bool(True),
                                    tausSignificance = cms.InputTag('tausSignificance', 'METCovariance'),
                                    saveMap = cms.bool(saveMapForTraining),
                                    permuteLeptonsWithinPlugin = cms.bool(True)
                                    )
