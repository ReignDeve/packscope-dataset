# PackScope — Supermarket Packaging Dataset

PackScope is a small, student-created image dataset of supermarket product packaging. Each photograph shows one main product package, annotated with a bounding box and a packaging-type class, and is described by structured per-image metadata (product, brand, category, material, quantity, photographer, annotator, capture details).

The dataset was created for a university course on research data management. It demonstrates object-detection annotations, structured metadata and FAIR data publication.

## At a glance

| Property                  | Value                                                                         |
| ------------------------- | ----------------------------------------------------------------------------- |
| Modality                  | RGB photographs (JPEG)                                                        |
| Number of images          | 33                                                                            |
| Number of brands          | 19                                                                            |
| Annotation                | One bounding box around the main package per image, with packaging-type class |
| Annotation format         | YOLO object detection (`.txt`, normalized coordinates)                        |
| Number of classes         | 9                                                                             |
| Metadata                  | `metadata.csv` (UTF-8, comma-separated, one row per image, 16 fields)         |
| Language of product names | Mostly German (as printed on the package)                                     |
| Capture devices           | iPhone 15 Pro (`IMG_0001`–`0021`), iPhone 14 Plus (`IMG_0022`–`0033`)         |
| Capture period            | 2026-10-30 – 2026-11-02                                                       |
| Collection location       | Supermarkets in Erlangen, Germany                                             |
| Authors                   | Hamza Jalil Mirza, Marius Bungert                                             |
| License                   | CC BY 4.0 (see [`LICENSE`](LICENSE))                                          |
| Version                   | 1.0                                                                           |
| DOI                       | [10.5281/zenodo.XXXXXXX]                                                      |

## Repository structure

```text
PackScope/
├── images/                  # 33 photographs, IMG_0001.jpg … IMG_0033.jpg
├── labels/                  # 33 YOLO annotation files, IMG_0001.txt … IMG_0033.txt
├── previews/                # Images with drawn bounding boxes (for inspection only)
├── scripts/
│   ├── make_previews.py     # Generates previews/
│   └── validate_dataset.py  # Checks consistency of images, labels and metadata
├── metadata.csv             # Per-image metadata
├── classes.txt              # Class names, line number = class ID
├── data.yaml                # Dataset config for YOLO tools (e.g. Ultralytics)
├── LICENSE                  # CC BY 4.0
├── CITATION.cff             # Citation information
└── README.md
```

Every image has exactly one label file and exactly one metadata row. Images, labels and metadata are linked via the shared basename (`IMG_0001.jpg` ↔ `labels/IMG_0001.txt` ↔ `metadata.csv` row with `image_id = IMG_0001.jpg`). All filenames use lowercase `.jpg`.

All images are stored in their display orientation (the EXIF rotation has been applied to the pixels), so bounding boxes are correct regardless of whether a tool reads EXIF orientation tags.

## Classes

Classes describe the **shape of the main external packaging**, not the product inside. IDs are defined in `classes.txt` and `data.yaml`.

| ID  | Class     | Definition                                        | Examples in dataset                         | Images |
| --- | --------- | ------------------------------------------------- | ------------------------------------------- | ------ |
| 0   | `can`     | Rigid cylindrical container (metal or composite)  | Soup cans, canned vegetables, Pringles tube | 9      |
| 1   | `bag`     | Flexible bag or pouch                             | Pasta, chips, flour, snack pouch            | 6      |
| 2   | `box`     | Rigid rectangular cardboard box                   | Pasta box                                   | 1      |
| 3   | `jar`     | Glass jar with wide opening and lid               | Olives, red cabbage, mayonnaise, jam        | 5      |
| 4   | `carton`  | Beverage carton (Tetra Pak style)                 | Long-life milk                              | 1      |
| 5   | `bottle`  | Container with a narrow neck                      | Whisky, squeeze bottle                      | 2      |
| 6   | `tub`     | Plastic cup or tub, open top sealed with foil/lid | Skyr, pudding, spreadable butter            | 5      |
| 7   | `tube`    | Squeezable tube                                   | Mayonnaise tube                             | 1      |
| 8   | `wrapper` | Flat wrapping or sealed flat tray pack            | Butter block in paper, sliced cold cuts     | 3      |

**Edge cases:** A composite can (e.g. Pringles) counts as `can`. A flexible pouch counts as `bag`. A sealed plastic tray with film lid counts as `wrapper`. A plastic squeeze bottle counts as `bottle`. Such cases are also marked in the `notes` column of `metadata.csv`.

**Class imbalance:** The distribution is strongly unbalanced (`box`, `carton` and `tube` have only one example each). The dataset is not suitable for training a robust detector without further data.

## Annotation format

Each file in `labels/` contains one line:

```text
<class_id> <x_center> <y_center> <width> <height>
```

All values are normalized to the image width and height (0–1). The box encloses the complete visible main package, including lid or cap.

**Annotation guidelines:**

- Exactly **one** object is annotated per image: the main package held in hand or placed in the centre.
- Other packages that are partially visible (e.g. shelf background, second package in `IMG_0005`) are intentionally **not** annotated. The dataset is therefore not suitable for multi-object detection as is.
- Boxes were drawn manually with [annotation tool, e.g. LabelImg / CVAT / Roboflow] and checked visually by a second person.

## Metadata schema

`metadata.csv` is UTF-8 encoded (without BOM), comma-separated, with one header row. Fields containing commas are enclosed in double quotes. Missing information is recorded as `unknown`.

| Field                 | Description                                                   | Example                                       |
| --------------------- | ------------------------------------------------------------- | --------------------------------------------- |
| `image_id`            | Image filename                                                | `IMG_0001.jpg`                                |
| `brand`               | Brand as printed on the package                               | `Erasco`                                      |
| `product_name`        | Product name as printed on the package                        | `Hühner Nudel-Topf`                           |
| `product_category`    | Main category (controlled list, see below)                    | `preserved food`                              |
| `product_subcategory` | Free-text detail                                              | `soup`                                        |
| `material`            | Main packaging material (controlled list, see below)          | `metal`                                       |
| `packaging_type`      | Packaging class, identical to the bbox class                  | `can`                                         |
| `net_quantity`        | Labelled quantity with unit                                   | `400 g`                                       |
| `photographer`        | Person who took the photo                                     | `Hamza Jalil Mirza`                           |
| `annotator`           | Person(s) who drew and checked the bounding box               | `Hamza Jalil Mirza, Marius Bungert`           |
| `capture_date`        | Date of capture (ISO 8601, `YYYY-MM-DD`)                      | `2026-10-30`                                  |
| `capture_setting`     | How the package was photographed (controlled list, see below) | `on_shelf`                                    |
| `device`              | Camera device                                                 | `iPhone 15 Pro`                               |
| `width`               | Image width in pixels                                         | `3024`                                        |
| `height`              | Image height in pixels                                        | `4032`                                        |
| `notes`               | Optional remarks on edge cases or image content               | `Composite (cardboard) can classified as can` |

**Controlled vocabularies:**

| Field              | Allowed values                                                                                                        |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `product_category` | `preserved food` (cans and jars), `dry goods`, `dairy`, `spread`, `condiment`, `snack`, `beverage`, `meat product`    |
| `material`         | `metal`, `glass`, `plastic`, `paper`, `cardboard`, `composite`                                                        |
| `packaging_type`   | `can`, `bag`, `box`, `jar`, `carton`, `bottle`, `tub`, `tube`, `wrapper`                                              |
| `capture_setting`  | `handheld` (held in hand), `on_shelf` (standing on the store shelf), `on_surface` (placed on floor, counter or table) |

## Content overview

- **33 products** from **19 brands**, all photographed in German supermarkets.
- Product range: preserved food (cans and jars), pasta and flour, dairy products, butter and spreads, condiments, snacks, beverages and meat products.
- The same product category appears in three different packaging types: mayonnaise in a jar (`IMG_0026`), a squeeze bottle (`IMG_0027`) and a tube (`IMG_0028`). `IMG_0026` and `IMG_0028` are the same product (Thomy).

**Capture settings:**

| `capture_setting` | Images                                                  | Count |
| ----------------- | ------------------------------------------------------- | ----- |
| `handheld`        | `IMG_0002`–`0007`, `IMG_0009`–`0021`, `IMG_0032`–`0033` | 21    |
| `on_shelf`        | `IMG_0001`, `IMG_0008`                                  | 2     |
| `on_surface`      | `IMG_0022`–`0031`                                       | 10    |

**Capture sessions:**

| Images                | Date       | Photographer      | Device         | Original resolution |
| --------------------- | ---------- | ----------------- | -------------- | ------------------- |
| `IMG_0001`–`IMG_0021` | 2026-10-30 | Hamza Jalil Mirza | iPhone 15 Pro  | 3024 × 4032         |
| `IMG_0022`–`IMG_0033` | 2026-11-02 | Marius Bungert    | iPhone 14 Plus | 1200 × 1600         |

All images are portrait orientation except `IMG_0005` (landscape).

## Collection method

1. All products were photographed inside supermarkets in Erlangen in two sessions (see above): session 1 with an iPhone 15 Pro, session 2 with an iPhone 14 Plus.
2. Products were chosen by convenience to cover as many packaging types as possible. No sampling was done.
3. No people are identifiable in the images. Hands and in some cases feet/shoes are visible.
4. Metadata was transcribed from the visible packaging. Quantities not readable on the photo were looked up on the product or recorded as `unknown`.
5. Bounding boxes were drawn by Hamza Jalil Mirza and checked by Marius Bungert (both listed in the `annotator` column: Hamza Jalil Mirza, Marius Bungert).

**Quality control** (automated with `scripts/validate_dataset.py`):

- Every image has exactly one label file and one metadata row.
- All class IDs are in the range 0–8 and match `classes.txt`.
- All box coordinates lie within [0, 1].
- `packaging_type` in `metadata.csv` matches the class ID in the label file.
- All values in controlled fields use the allowed vocabulary.
- All boxes were checked visually on the preview images in `previews/` (generated with `scripts/make_previews.py`).

## Usage

The dataset can be loaded directly with YOLO tools such as Ultralytics using `data.yaml`:

```bash
yolo detect train data=data.yaml model=yolov8n.pt epochs=50
```

**Note:** There is no official train/validation/test split. In `data.yaml`, `train` and `val` point to the same folder, which is only suitable for pipeline tests. For real experiments, create your own split.

Metadata can be read with any CSV library, for example:

```python
import pandas as pd
meta = pd.read_csv("metadata.csv")
print(meta["packaging_type"].value_counts())
```

To check the dataset or regenerate the previews (requires `pillow` and `pyyaml`):

```bash
python scripts/validate_dataset.py
python scripts/make_previews.py
```

## Limitations

- **Very small:** 33 images, one object per image.
- **Unbalanced classes:** some classes have only one example.
- **Convenience sample:** products, brands and stores reflect what was available, not the market.
- **Two capture sessions:** the sessions differ in device, resolution and setting (mostly handheld in front of shelves vs. mostly placed on the floor or a counter with a plain background).
- **Regional bias:** German supermarkets, German product labels.
- **Single-object annotation:** background packages are not annotated.

Intended use: teaching, demonstration and testing of dataset pipelines. Not intended as a benchmark.

## License

The photographs, annotations and metadata are licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). See [`LICENSE`](LICENSE).

Product names, brands, logos and package designs shown in the images are trademarks of their respective owners. The license covers only the rights held by the dataset authors.

## Citation

> Hamza Jalil Mirza, Marius Bungert (2026). _PackScope: Supermarket Packaging Dataset_ (Version 1.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.XXXXXXX

See also [`CITATION.cff`](CITATION.cff).

## FAIR self-assessment

| Principle         | How it is addressed                                                                                                                                                                           | Rating |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| **Findable**      | Persistent DOI via Zenodo, descriptive title, keywords (packaging, object detection, supermarket, YOLO, bounding box), rich metadata in the Zenodo record                                     | ●●●○   |
| **Accessible**    | Openly downloadable from Zenodo via HTTPS without login, metadata remains available even if files were removed                                                                                | ●●●●   |
| **Interoperable** | Standard formats (JPEG, CSV, YAML, YOLO TXT), documented schema, controlled vocabularies for category, material, packaging type and capture setting. No formal ontology used                  | ●●●○   |
| **Reusable**      | Clear license (CC BY 4.0), documented collection method, annotation guidelines, provenance per image (photographer, annotator, date, device), limitations stated, automated validation script | ●●●○   |

Main weaknesses: no standard vocabulary/ontology (e.g. GS1 product categories), small size and no official data split.

## Changelog

- **1.0** (2026-11-04): First public release.

## Contact

Marius Bungert - mariusbungert@gmx.de
