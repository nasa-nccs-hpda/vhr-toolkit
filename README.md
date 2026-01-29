# vhr-toolkit

- GitHub repo: https://github.com/nasa-nccs-hpda/vhr-toolkit
- Documentation: https://nasa-nccs-hpda.github.io/vhr-toolkit

## Container Download

The CPU-only version of the vhr-toolkit container can be downloaded with:

```bash
singularity build --sandbox /lscratch/$USER/container/vhr-toolkit docker://nasanccs/vhr-toolkit:pytorch
```

## Quickstart

To run the entire workflow for a single test scene:

```bash
singularity exec --nv -B /explore,/panfs,/css,/nfs4m /explore/nobackup/projects/ilab/containers/vhr-toolkit-latest python /usr/local/ilab/vhr-toolkit/vhr_toolkit/view/vhrToolkit.py -o vhr-toolkit-output --scenes_in_file tests/catalog_1030010003A81D00.txt | tee catalog_1030010003A81D00.log
```

## Contributing

Please see our [guide for contributing to vhr-toolkit](CONTRIBUTING.md). Contributions
are welcome, and they are greatly appreciated! Every little bit helps, and credit will
always be given.

You can contribute in many ways:

### Report Bugs

Report bugs at https://github.com/nasa-nccs-hpda/vhr-toolkit/issues.

If you are reporting a bug, please include:
- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and
"help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is
open to whoever wants to implement it.

### Write Documentation

vhr-toolkit could always use more documentation, whether as part of the official vhr-cloudmask docs,
in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/nasa-nccs-hpda/vhr-toolkit/issues.

If you are proposing a feature:
- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)
