#!/usr/bin/python

import argparse
import csv
import logging
from pathlib import Path
import sys

from core.model.DgFile import DgFile

from evhr.model.EvhrToA import EvhrToA
# from pyCCDC.model.CCDCPipeline import CCDCPipeline
from srlite.model.SrliteWorkflow import SrliteWorkflow

# from vhr_cloudmask.model.pipelines.cloudmask_cnn_pipeline import \
#     CloudMaskPipeline


# -----------------------------------------------------------------------------
# main
#
# vhr-toolkit/view/vhrToolkit.py -o /explore/nobackup/people/rlgill/SystemTesting/testILTK --scenes_in_file /explore/nobackup/projects/ilab/projects/vhr-toolkit/testing/evhr/toa_clv_test_alaska_cloud.csv
#
# TODO: EvhrToA needs an accessor for _outDir, _toaDir.
# TODO: EvhrToA.__init__() outDir s/b of type Path.
# TODO: EvhrToA.run() return list of ToAs produced?
# -----------------------------------------------------------------------------
def main():
    
    # ---
    # Parse input arguments.
    # ---
    args = parseArgs()

    # ---
    # Logging
    # ---
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    # ---
    # Make DgFiles from the input scenes. 
    # ---
    scenes = args.scenes

    # if args.scenes_in_file:

    #     with open(args.scenes_in_file, newline='') as csvFile:

    #         reader = csv.reader(csvFile)
    #         scenes = [Path(scene[0]) for scene in reader]

    # dgScenes = scenesToDgFiles(scenes, logger)
    
    # ---
    # EVHR
    # ---
    logger.info('Running EVHR.')
    toa = EvhrToA(args.o, args.dem, args.pan_res, args.pan_sharpen, logger)
    # toa.run(dgScenes)
    toaDir = Path(toa._toaDir)
    toaDirNum = int(toaDir.name.split('-')[0])
    toas = toaDir.glob('*-toa.tif')

    # ---
    # EVHR -> CloudMaskPipeline
    # ---
    logger.info('Running CloudMaskPipeline.')
    cMaskDirNum = toaDirNum + 1
    cMaskDir = Path(args.o) / (str(cMaskDirNum) + '-masks')
    cMaskDir = Path(args.o) / (str(cMaskDirNum) + '-masks/5-toas')
    cMaskDir.mkdir(exist_ok=True)
    toaRegex = [str(toaDir / '*-toa.tif')]
    # cmpl = CloudMaskPipeline(output_dir=cMaskDir, inference_regex_list=toaRegex)
    # cmpl.predict()

    # ---
    # EHVR -> CCDC
    # ---
    logger.info('Running CCDC.')
    ccdcDirNum = cMaskDirNum + 1
    # Toggle these two to cause 'Invalid Coordinate' error (Mel reprojected the original)
    ccdcDir = Path(args.o) / (str(ccdcDirNum) + '-ccdc/reprojected')
    # ccdcDir = Path(args.o) / (str(ccdcDirNum) + '-ccdc')
    ccdcDir.mkdir(exist_ok=True)
    expCcdc = [ccdcDir / f.name.replace('-toa', '-toa_ccdc') for f in toas]
    
    # if not all([f.exists() for f in expCcdc]):
        
    #     ccdc = CCDCPipeline(input_dir=toaDir, output_dir=ccdcDir)
    #     ccdc.run()

    # ---
    # EVHR + Cloud Mask + CCDC -> SRL
    # ---
    logger.info('Running SR Lite.')
    srlDirNum = ccdcDirNum + 1
    srlDir = Path(args.o) / (str(srlDirNum) + '-srl')
    srlDir.mkdir(exist_ok=True)

    # import pdb
    # pdb.set_trace()
    srl = SrliteWorkflow(output_dir=srlDir,
                         toa_src=toaDir,
                         target_dir=ccdcDir,
                         cloudmask_dir=cMaskDir,
                         regressor='rma',
                         debug=1,
                         pmask='True',
                         cloudmask='True',
                         csv='True',
                         band8='True',
                         clean='False',
                         toa_suffix='-toa.tif',
                         target_suffix='-toa_ccdc.tif',
                         cloudmask_suffix='-toa.cloudmask.tif',
                         logger=logger)

    srl.processToas()
    
# -----------------------------------------------------------------------------
# parseArgs
# -----------------------------------------------------------------------------
def parseArgs() -> argparse.Namespace:
    
    desc = 'Use this application to run the VHR Toolkit.'
    parser = argparse.ArgumentParser(description=desc)

    # ---
    # Universal Parameters
    # ---
    parser.add_argument('-o',
                        default='.',
                        help='Path to output directory')

    # ---
    # EVHR Parameters
    # ---
    parser.add_argument('--dem',
                        type=Path,
                        required=False,
                        help='Fully-qualified path to DEM footprints shape '
                             ' file.')

    parser.add_argument('--pan_res',
                        type=float,
                        default=1,
                        choices=[0.5, 1],
                        help='The resolution, in meters, of panchromatic '
                             'output images')

    parser.add_argument('--pan_sharpen',
                        action='store_true',
                        help='Apply panchromatic sharpening to the output '
                             'ToA images.')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--scenes',
                       type=Path,
                       nargs='*',
                       help='Fully-qualified path to scene files')

    group.add_argument('--scenes_in_file',
                       type=Path,
                       help='Fully-qualified path to CSV file containing a '
                            'list of scene files')

    # ---
    # VHR Cloud Mask Parameters
    # ---
    
    # ---
    # CCDC Parameters
    # ---
    
    # ---
    # SR-lite Parameters
    # ---
    
    # ---
    # Parse
    # ---
    args = parser.parse_args()
        
    return args
    
# -----------------------------------------------------------------------------
# scenesToDgFiles
# -----------------------------------------------------------------------------
def scenesToDgFiles(scenes: list, logger: logging.RootLogger) -> list:
    
    dgScenes = []

    for s in scenes:

        if not s.exists():
            logger.warning('Scene, ' + str(s) + ' does not exist.')

        else:
            dgScenes.append(DgFile(str(s)))
            
    return dgScenes

# -----------------------------------------------------------------------------
# Invoke the main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
