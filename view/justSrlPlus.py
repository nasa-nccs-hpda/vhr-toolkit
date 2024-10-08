#!/usr/bin/python

import csv
import logging
from pathlib import Path
import sys

from core.model.DgFile import DgFile
from evhr.model.EvhrToA import EvhrToA
from pyCCDC.model.CCDCPipeline import CCDCPipeline
from srlite.model.SrliteWorkflow import SrliteWorkflow

from vhr_cloudmask.model.pipelines.cloudmask_cnn_pipeline import \
    CloudMaskPipeline


# -----------------------------------------------------------------------------
# main
#
# vhr-toolkit/view/justSrlPlus.py
# -----------------------------------------------------------------------------
def main():
    
    outDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK')

    srlDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/8-srl')

    toaDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/5-toas')
    
    ccdcDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/7-ccdc')
        
    cMaskDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/6-masks')

    scenesFile = Path('/explore/nobackup/projects/ilab/projects/vhr-toolkit/' + 
                      'testing/evhr/toa_clv_test_alaska_cloud.csv')

    # Scenes
    with open(scenesFile, newline='') as csvFile:

        reader = csv.reader(csvFile)
        scenes = [Path(scene[0]) for scene in reader]

    dgScenes = []

    for s in scenes:

        if not s.exists():
            logger.warning('Scene, ' + str(s) + ' does not exist.')

        else:
            dgScenes.append(DgFile(str(s)))
         
    # ---
    # Logging
    # ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    # EVHR
    toa = EvhrToA(outDir)
    toa.run(dgScenes)
    
    # Cloud Mask
    toaRegex = [str(toaDir / '*-toa.tif')]
    cmpl = CloudMaskPipeline(output_dir=cMaskDir, inference_regex_list=toaRegex)
    cmpl.predict()
       
    # CCDC
    ccdc = CCDCPipeline(input_dir=toaDir, output_dir=ccdcDir)
    ccdc.run()
    
    # SRL
    srl = SrliteWorkflow(output_dir=srlDir,
                         toa_src=toaDir,
                         target_dir=ccdcDir,
                         cloudmask_dir=cMaskDir)

# -----------------------------------------------------------------------------
# Invoke the main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
