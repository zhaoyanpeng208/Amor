# Molecular Representation Benchmarking

This repository accompanies the study on benchmarking molecular representation–prediction pipelines for drug discovery.

The GitHub repository is intentionally lightweight. It mainly contains scripts for **dataset splitting**, **statistical visualization**, and **figure generation**. Because the complete benchmark datasets and full model/code packages are too large to host conveniently on GitHub, they are archived separately in **Zenodo**.

## Repository structure

```text
.
├── README.md
├── code_for_plot.zip
├── data_split.py
├── figure1.png
└── plot_statistical_figure.py
```

### Files

- **`data_split.py`**  
  Script used to generate the benchmark train/validation/test partitions.  
  In the main benchmark, each dataset was split into training, validation, and test sets at an 80%/10%/10% ratio. Five independent dataset partitions were generated using the seeds:

  ```text
  29, 37, 42, 49, 51
  ```

  For each seed, all molecular representation–prediction pipelines were evaluated using the same data partition.

- **`plot_statistical_figure.py`**  
  Script used to generate the statistical comparison figure based on the cross-dataset benchmark results, including the average-rank summary and pairwise statistical-comparison visualization.

- **`code_for_plot.zip`**  
  Archive containing additional plotting scripts used to generate figures in the manuscript and supplementary materials.

- **`figure1.png`**  
  Overview figure associated with the benchmark workflow.

## Benchmark overview

The study evaluates **31 molecular representation–prediction pipelines** across **17 drug-discovery-related datasets**, covering five application categories:

1. Physiological property prediction
2. Biophysical property prediction
3. Physicochemical property prediction
4. Quantum-mechanical property prediction
5. Antiviral activity prediction

The benchmark includes fixed and learned molecular representations based on 1D, 2D, 3D, and hybrid molecular information.

For reproducibility, repeated dataset partitions were generated with the five predefined seeds listed above, and the same split corresponding to each seed was used for all evaluated pipelines.

## Data and full code availability

Due to the large size of the benchmark datasets, trained-model resources, intermediate results, and complete code packages, these files are **not hosted directly in this GitHub repository**.

The complete resources are archived in **Zenodo** for long-term preservation and reproducibility.

**Zenodo archive:**  
`[ZENODO_URL_TO_BE_ADDED]`

**Zenodo DOI:**  
`[ZENODO_DOI_TO_BE_ADDED]`

The Zenodo archive contains:

- benchmark datasets;
- complete model and training code;
- dataset split files;
- raw and processed benchmark results;
- scripts required for reproducing the analyses and figures;
- additional supplementary resources.

Users who wish to reproduce the complete benchmark should first download the corresponding Zenodo archive.

## Recommended reproduction workflow

1. Clone this GitHub repository.
2. Download the complete datasets and code packages from Zenodo.
3. Use `data_split.py` to reproduce the predefined dataset partitions, if needed.
4. Run the corresponding benchmark/model code from the Zenodo archive.
5. Use the plotting scripts in `code_for_plot.zip` and `plot_statistical_figure.py` to reproduce the figures and statistical summaries.

## AMoR platform

The benchmark results are also integrated into the AMoR platform for molecular representation evaluation, representation generation, and molecular property prediction:

https://amor.bioinforai.tech/

## License

Please refer to the licenses of the original datasets and individual molecular representation/model implementations. The scripts provided in this repository are intended for academic research and reproducibility purposes.
