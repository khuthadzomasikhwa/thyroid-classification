# Thyroid disease classification

This project classifies one clinic record as **no thyroid problem**, **hypothyroid**, or **hyperthyroid**.

The records are from the Garvan Institute, Sydney, 1984 to early 1987. Quinlan documented the file and donated it in 1986.

This is a classification of historical records. It is not a diagnosis for a real patient.

## Result

The model kept for new records is a **random forest trained with SMOTE**.

On the locked test set (1,536 records, opened once at the end):

- Macro F1: **0.94**
- Accuracy: **0.99**

Stratified 5-fold on the training rows gave a macro F1 of 0.940, with a standard deviation of 0.009. The score stayed steady across the five folds.

A most-frequent baseline scored 0.31 macro F1, because it never selects either disease class.

## What is included

| Path | What it is |
| --- | --- |
| `thyroid_classification.ipynb` | Cleaning, column checks, training, validation, and the locked test |
| `app/` | A page that classifies one record with the saved model |
| `data/thyroid-disease/thyroid0387.data` | The raw UCI file |
| `data/thyroid_dataset_ready.csv` | The cleaned table used for training |
| `data/thyroid_dataset_model.joblib` | The saved random forest, imputer, and scaler |

## Data decisions

The raw file has 9,172 records and 30 columns. After keeping only the three classes, 7,679 records remain.

The split is stratified, 80% train and 20% test, and it happens before imputation and scaling. The training set has 6,143 records. The test set has 1,536.

The model reads **25 input columns** after sex is encoded. The target stays in the cleaned table as the answer. It is not an input.

Left out of the model: TBG and its measured flag, referral source, hypopituitary, goitre, and the record number. An age above 100 is treated as missing. A missing age or blood test is filled with the training median. A blank blood test is marked as not measured.

Logistic regression and random forest were both trained with SMOTE and with class weights. The same four models went through stratified 5-fold cross-validation. The test matrices are the full training fit on the locked test, not the cross-validation folds.

## Run the page

From `app/web`:

```powershell
npm install
npm run build
npm start
```

Open http://127.0.0.1:8765.

Python packages used by the notebook and the page: `pandas`, `numpy`, `scikit-learn`, `imbalanced-learn`, `matplotlib`, `joblib`.

Sex and the clinical questions have to be answered. Age and the blood tests can be left blank. Age must be a whole number. An age above 100 is left out.

## Source

Quinlan, R. (1986). *Thyroid Disease* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5D010
