#!/usr/bin/python

import argparse
import csv
import logging
from pathlib import Path
import sys

from osgeo import gdal

from core.model.DgFile import DgFile

from evhr.model.EvhrToA import EvhrToA
from pyCCDC.model.CCDCPipeline import CCDCPipeline
from srlite.model.SrliteWorkflow import SrliteWorkflow

from vhr_cloudmask.model.pipelines.cloudmask_cnn_pipeline import \
    CloudMaskPipeline


# -----------------------------------------------------------------------------
# main
#
# vhr-toolkit/vhr_toolkit/view/vhrToolkit.py -o /explore/nobackup/people/rlgill/SystemTesting/testILTK --scenes_in_file /explore/nobackup/projects/ilab/projects/vhr-toolkit/testing/evhr/toa_clv_test_alaska_cloud.csv  # noqa: E501
#
# vhr-toolkit/vhr_toolkit/view/vhrToolkit.py -o /explore/nobackup/projects/ilab/ILTK-testing-output/214 --scenes_in_file /explore/nobackup/projects/ilab/ILTK-testing-output/214/toa_clv_test_alaska_cloud_214.csv  # noqa: E501
#
# TODO: EvhrToA needs an accessor for _outDir, _toaDir.
# TODO: EvhrToA.__init__() outDir s/b of type Path.
# -----------------------------------------------------------------------------
def main():

    # ---
    # Parse input arguments.
    # ---
    args = parseArgs()
    outDir: Path = args.o

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

    if args.scenes_in_file:

        with open(args.scenes_in_file, newline='') as csvFile:

            reader = csv.reader(csvFile)
            scenes = [Path(scene[0]) for scene in reader]

    dgScenes = scenesToDgFiles(scenes, logger)

    # ---
    # EVHR
    # ---
    logger.info('Running EVHR.')

    toa = EvhrToA(str(outDir),
                  args.dem,
                  args.pan_res,
                  args.pan_sharpen,
                  logger)

    toas: list = toa.run(dgScenes)
    toaDir = Path(toa.toaDir)
    toaDirNum = int(toaDir.name.split('-')[0])
    toas = toaDir.glob('*-toa.tif')

    # ---
    # Process ToA files.
    # ---
    for toaFile in toas:

        logger.info('Processing ' + str(toaFile))
        processToaFile(
            toaFile, toaDir, toaDirNum, outDir, args.gee_key, logger)


# -----------------------------------------------------------------------------
# getBandPairs
# -----------------------------------------------------------------------------
def getBandPairs(toaFile: Path, ccdcFile: Path) -> list:

    if ccdcFile.name.endswith('_ccdc.tif'):

        bandPairs = [['BLUE', 'BAND-B'], ['GREEN', 'BAND-G'],
                     ['RED', 'BAND-R'], ['NIR', 'BAND-N']]

        bandPairsExtra = [['BLUE', 'BAND-C'], ['GREEN', 'BAND-Y'],
                          ['RED', 'BAND-RE'], ['NIR', 'BAND-N2']]

    elif ccdcFile.name.endswitth('-ccdc.tif'):

        bandPairs = [['blue_ccdc', 'BAND-B'], ['green_ccdc', 'BAND-G'],
                     ['red_ccdc', 'BAND-R'], ['nir_ccdc', 'BAND-N']]

        bandPairsExtra = [['blue_ccdc', 'BAND-C'], ['green_ccdc', 'BAND-Y'],
                          ['red_ccdc', 'BAND-RE'], ['nir_ccdc', 'BAND-N2']]

    else:
        raise RuntimeError('Unable to map bands for ' + str(ccdcFile))

    # How many bands in the ToA?
    numBands: int = gdal.Open(str(toaFile), gdal.GA_ReadOnly).RasterCount

    if numBands == 8:

        bandPairs += bandPairsExtra

    elif numBands != 4:

        raise RuntimeError('Expected 4 or 8 bands, but found ' + str(numBands))

    return bandPairs


# -----------------------------------------------------------------------------
# processToaFile
# -----------------------------------------------------------------------------
def processToaFile(toaFile: Path,
                   toaDir: Path,
                   toaDirNum: int,
                   outDir: Path,
                   geeKey: str = None,
                   logger: logging.RootLogger = None) -> None:

    # ---
    # EVHR -> CloudMaskPipeline
    # ---
    logger.info('Running CloudMaskPipeline.')
    cMaskDirNum = toaDirNum + 1
    cMaskDir = outDir / (str(cMaskDirNum) + '-masks')
    cMaskDir.mkdir(exist_ok=True)

    cmpl = CloudMaskPipeline(output_dir=cMaskDir,
                             inference_regex_list=[str(toaFile)])

    cmpl.predict()

    # ---
    # EHVR -> CCDC
    # ---
    logger.info('Running CCDC.')
    ccdcDirNum = cMaskDirNum + 1
    ccdcDir = outDir / (str(ccdcDirNum) + '-ccdc')
    ccdcDir.mkdir(exist_ok=True)
    ccdc = CCDCPipeline(
        input_dir=toaDir,
        output_dir=ccdcDir,
        gee_key=geeKey)
    ccdcFile: Path = ccdc.run(toaFile)[0]

    # ---
    # Get band pairs for SRL.
    # ---
    print("BEFORE BAND PAIRS")
    bandPairs: list = getBandPairs(toaFile, ccdcFile)
    print("THIS ARE MY BAND PAIRS")

    # ---
    # EVHR + Cloud Mask + CCDC -> SRL
    # ---
    logger.info('Running SR Lite.')
    srlDirNum = ccdcDirNum + 1
    srlDir = outDir / (str(srlDirNum) + '-srl')
    srlDir.mkdir(exist_ok=True)

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
                         clean='True',
                         cloudmask_suffix='-toa_cloudmask.tif',
                         target_suffix='-toa_ccdc.tif',
                         bandpairs=str(bandPairs),
                         logger=logger)

    srl.processToa(toaFile)


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
                        type=Path,
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
    parser.add_argument('--gee-key',
                        type=Path,
                        default=None,
                        required=False,
                        dest='gee_key',
                        help='Path to GEE location')

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
