============================================================================================================================
Surface reflectance from commercial very high resolution multispectral imagery estimated empirically with synthetic Landsat
============================================================================================================================

.. image:: https://github.com/nasa-nccs-hpda/vhr-toolkit/actions/workflows/lint.yml/badge.svg
        :target: https://github.com/nasa-nccs-hpda/vhr-toolkit/actions/workflows/lint.yml

Background
------------

Scientific analysis of changes of the Earth's land surface benefit from well-characterized, science quality 
remotely sensed data. This data quality is the result of models that estimate and remove atmospheric 
constituents and account for sun-sensor geometry.  Top-of-atmosphere (TOA) reflectance in commercial 
very high resolution (< 5 m; VHR) spaceborne imagery routinely varies for unchanged surface features 
because of signal variation from the combined effects of atmospheric haze and a range of sun-sensor 
geometric scenarios of acquisitions. Consistency from surface reflectance (SR) versions of this imagery 
must be sufficient to identify and track the change or stability of fine-scale features that, though small, 
may be widely distributed across remote domains, and serve as key indicators of critical broad-scale 
environmental change. Currently commercial SR products are available, but typically the model employed 
is proprietary and the costs for using these products over a large domain can be significant. 

Here we provide an open-source workflow for the scientific community for fine-scaled empirical 
estimation of surface reflectance from multispectral VHR imagery using reference from 
synthetically-derived coincident Landsat-based surface reflectance.  

SR\ :sub:`VHR`: empirical estimation of VHR surface reflectance (SR-lite) 
----------------------------------------------------------------------------

The workflow for estimating surface reflectance for commercial VHR multispectral imagery (SR\ :sub:`VHR`).

![fig1_v3 (1)](https://github.com/user-attachments/assets/f3a6f82c-56bd-4b14-b3d2-74f55be47514)

 Workflow Contributors | Role | Affiliation | 
| ---------------- | ---------------- | ---------------- |
| Paul M .Montesano |  Author ; Evaluator | NASA Goddard Space Flight Center Data Science Group |
| Matthew J. Macander |   Author ; Evaluator | Alaska Biological Research, Inc. |
| Jordan A. Caraballo-Vega  |  Developer | NASA Goddard Space Flight Center Data Science Group |
| Melanie J. Frost |  Author ; Evaluator | NASA Goddard Space Flight Center Data Science Group |
| Jian Li |  Developer | NASA Goddard Space Flight Center Data Science Group |
| Glenn S. Tamkin  |  Developer | NASA Goddard Space Flight Center Data Science Group |
| Mark L. Carroll |  PI | NASA Goddard Space Flight Center Data Science Group (Lead)|


