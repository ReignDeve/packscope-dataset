# PackScope — Supermarket Packaging Dataset

PackScope is a small, student-created image dataset of supermarket product packaging. It is designed to demonstrate object detection annotations and structured dataset metadata.

> **Status:** Collection in progress. Replace the placeholders below and update the statistics before publishing on Zenodo.

## Dataset overview

| Property | Description |
| --- | --- |
| Modality | Images (JPEG/PNG) |
| Target size | 30–40 photographs |
| Annotation | One bounding box around the main packaging object in each image |
| Classes | `bottle`, `can`, `box`, `jar`, `carton`, `bag` |
| Metadata | Product name, brand, product category, packaging material, net quantity, packaging type |
| Annotation format | YOLO object detection text files (normalized coordinates) |
| Metadata format | CSV (UTF-8) |
| Collection location | [City / country, if appropriate] |
| Collection date | [Month and year] |
| Authors | [Author 1], [Author 2] |
| Zenodo DOI | [Add DOI after publication] |

## Dataset structure

```text
PackScope/
├── images/
│   ├── IMG_001.jpg
│   └── ...
├── annotations/
│   ├── IMG_001.txt
│   └── ...
├── previews/                 # Optional, not required for model training
│   └── IMG_001_annotated.jpg
├── metadata.csv
├── classes.txt
├── README.md
└── LICENSE
```

The basename of each annotation file must match its image (for example, `IMG_001.jpg` and `IMG_001.txt`). Each `metadata.csv` row references an image using its filename.

## Annotation schema

Each image has a bounding box around its main visible product package, including the complete package where possible. Images should not be tightly cropped before annotation.

**YOLO format** (`annotations/IMG_001.txt`):

```text
<class_id> <x_center> <y_center> <width> <height>
```

Bounding box values are normalized to the image dimensions and lie between 0 and 1. The coordinates describe the visible package, not the whole shelf or surrounding products.

**Class IDs** (also listed in `classes.txt`):

```text
0 bottle
1 can
2 box
3 jar
4 carton
5 bag
```

Where a product could fit multiple categories, use the shape of its **main external packaging**. Keep class names and IDs consistent throughout the dataset. If the proposed classes do not cover a collected object, revise and document the label scheme **before** annotating it; do not assign a misleading class.

## Metadata schema

The UTF-8 file `metadata.csv` has one row per image and the following columns:

| Field | Meaning | Example |
| --- | --- | --- |
| `image_id` | Image filename | `IMG_001.jpg` |
| `product_name` | Product name on package | `Mineral Water` |
| `brand` | Brand on package | `Example Brand` |
| `product_category` | Broad product group | `Beverage` |
| `material` | Main external packaging material | `Plastic` |
| `net_quantity` | Labeled quantity including unit | `500 ml` |
| `packaging_type` | Packaging shape, matching the bbox class | `bottle` |

Use `unknown` where information is not legible or available. The row shown above is an illustrative example, **not an actual collected sample**.

## Collection and quality control

1. Photograph products with permission where required, preferably with the main package clearly visible and some surrounding background.
2. Exclude identifiable people and other personal information from photographs.
3. Give each image a unique filename, then record its metadata from the visible packaging.
4. Draw one tight bounding box around the main package and assign the appropriate class.
5. Export the annotations in YOLO format and check that class IDs match `classes.txt`.
6. Verify that every image has a matching annotation and metadata row, that boxes lie within image boundaries, and that no duplicate filenames exist.

**Collection method:** [Describe where and how the photographs were taken, device(s) used, and any sampling decisions.]

**Dataset size and class counts:** [Replace with actual counts after collection.]

## Limitations

PackScope is a small, convenience-sampled dataset and is not intended to represent all packaging on the market. Product availability, brand selection, lighting, camera angle, background, and packaging shape may introduce bias. It is primarily suitable for demonstration, educational use, and testing dataset pipelines rather than benchmarking object detection systems.

## Reuse and citation

The original material to which the contributors hold the necessary rights is offered under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [`LICENSE`](LICENSE). Product names, brands and third-party trademarks remain the property of their respective owners. The license does not grant rights the contributors do not hold.

**Citation:** [Authors]. (*[Year]*). *PackScope: Supermarket Packaging Dataset* (Version 1.0) [Data set]. Zenodo. [DOI]

Replace the citation with the published Zenodo record information.

## FAIR considerations

- **Findable:** A descriptive title, keywords and a Zenodo DOI once published.
- **Accessible:** Publicly downloadable files from the Zenodo record if published as open access.
- **Interoperable:** Standard image formats, CSV and documented YOLO annotations and class IDs.
- **Reusable:** Metadata definitions, collection methodology, annotation guidelines and a clear license statement.

These are intended practices; assess the actual published dataset when preparing the presentation.
