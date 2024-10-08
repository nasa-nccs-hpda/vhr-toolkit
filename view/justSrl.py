#!/usr/bin/python

from pathlib import Path
import sys

from srlite.model.SrliteWorkflow import SrliteWorkflow


# -----------------------------------------------------------------------------
# main
#
# vhr-toolkit/view/justSrl.py
# -----------------------------------------------------------------------------
def main():
    
    srlDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/8-srl')

    toaDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/5-toas')
    
    ccdcDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/7-ccdc')
        
    cMaskDir = \
        Path('/explore/nobackup/people/rlgill/SystemTesting/testILTK/6-masks')

    srl = SrliteWorkflow(output_dir=srlDir,
                         toa_src=toaDir,
                         target_dir=ccdcDir,
                         cloudmask_dir=cMaskDir)

# -----------------------------------------------------------------------------
# Invoke the main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
