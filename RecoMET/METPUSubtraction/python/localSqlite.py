import FWCore.ParameterSet.Config as cms
def loadLocalSqlite(process, sqliteFilename, tag = 'JetCorrectorParametersCollection_Fall15_25nsV2_MC_AK4PFchs'):
    process.load("CondCore.DBCommon.CondDBCommon_cfi")
    from CondCore.DBCommon.CondDBSetup_cfi import *
    process.jec = cms.ESSource("PoolDBESSource",
          DBParameters = cms.PSet(
            messageLevel = cms.untracked.int32(0)
            ),
          timetype = cms.string('runnumber'),
          toGet = cms.VPSet(
          cms.PSet(
                record = cms.string('JetCorrectionsRecord'),
                tag    = cms.string(tag),
                label  = cms.untracked.string('AK4PFCHS')
                ),
          ), 
          connect = cms.string('sqlite:' + sqliteFilename)
    )
    ## add an es_prefer statement to resolve a possible conflict from simultaneous connection to a global tag
    process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jec')
