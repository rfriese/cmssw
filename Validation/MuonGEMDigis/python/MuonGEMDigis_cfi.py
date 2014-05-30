import FWCore.ParameterSet.Config as cms

gemDigiValidation = cms.EDAnalyzer('MuonGEMDigis',
	outputFile = cms.string(''),
	stripLabel= cms.InputTag('simMuonGEMDigis'),
	cscPadLabel = cms.InputTag('simMuonGEMCSCPadDigis'),
	cscCopadLabel = cms.InputTag('simMuonGEMCSCPadDigis','Coincidence') ,
	simInputLabel = cms.untracked.string('g4SimHits'),
	minPt = cms.untracked.double(5.),
	maxEta = cms.untracked.double(2.45),
	minEta = cms.untracked.double(1.55), 
	PlotBinInfo = cms.PSet(
			nBinGlobalZR = cms.untracked.vdouble(200,200,200,150,180,250), 
			RangeGlobalZR = cms.untracked.vdouble(564,572,786,794,794,802,110,260,170,350,100,350), 
  ),
	simTrackMatching = cms.PSet(
            verboseSimHit = cms.untracked.int32(0),
            simInputLabel = cms.untracked.string('g4SimHits'),
            # GEM digi matching:
            verboseGEMDigi = cms.untracked.int32(0),
            gemDigiInput = cms.untracked.InputTag("simMuonGEMDigis"),
            gemPadDigiInput = cms.untracked.InputTag("simMuonGEMCSCPadDigis"),
            gemCoPadDigiInput = cms.untracked.InputTag("simMuonGEMCSCPadDigis", "Coincidence"),
            minBXGEM = cms.untracked.int32(-1),
            maxBXGEM = cms.untracked.int32(1),
            matchDeltaStripGEM = cms.untracked.int32(1),
            gemDigiMinEta  = cms.untracked.double(1.5),
            gemDigiMaxEta  = cms.untracked.double(2.6),
            gemDigiMinPt = cms.untracked.double(5.0),
						EtaRangeForPhi = cms.untracked.vdouble( 1.5, 2.2, 1.6, 2.1, 1.6, 2.5),
  ),
)
