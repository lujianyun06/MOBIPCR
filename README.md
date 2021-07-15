# MOBIPCR: Effectient,Accurate,and Strict ML-Based Mobile Malware Detection
**Code of MOBIPCR**

This project need some envtools:

python2.7,  scikit-learn, androguard1.5,androbugs,mongodb

## NOTE: 
In order to avoid possible illegal infringement, the corresponding data set cannot be provided. Please download according to the paper.

### STEP1. Put apk info into mongodb

add_db.py: use this to extract features from apk and put it into db. it depends core2.py.

NOTE：this process need androguard1.5 and androbugs. but we make some modification on androbugs, specific as follows:
androbugs divides vulnerability levels into four categories, which are CRITICAL,WARNING,NOTICE and INFO. We only need CRITICAL and WARNING，so we should make a patch to shielding the other two vulnerabilities. This process is shown in androbugs.py and test_getvector.py.

### STEP2. Feature selection

1. create_optunits.py: this file is used to integrated opcodes for different types of apps，it will create two files: goodware_opt_units and badware_opt_units.

2. create_tioe.py: This file do CbTFIDF algorithmon on the above generated two files , the purpose of the opcode for dimensionality reduction preprocessing.
this process will generate opcodeslist which we need.

3. create_data.py: Generate characteristic matrix in first phase.

4. feature_selection.py Generate final characteristic matrix.

### STEP3. Hyperparameter selection

this project use 6 base models, which is Ada, KNN, SVM, LightGBM and GBC. we can use grid_search_BASEMODEL.py to select hyperparameter.

### STEP4. Model training

model_training.py: we can use this file to train models by hyperparameter we get above.

### STEP5. DES process

des2.py: we use this file to get an app's neighbors and base models that perform well on these neighbors.

In order to predict an app,speed up the process, we make some tricks: 

### STEP6.Stacking process

stacking_custom.py: stacking process, it depends CustomStackingModels.

CustomStackingModels.py Core stacking file.

### STEP7.Server for detection service

folder "detect_server" is a classic Django project, You can start it by learning Django's tutorial(https://docs.djangoproject.com/en/3.2/). 

### STEP8.Bridge APP

folder BridgeApp is a classic AndroidStudio project, You can start it by learning AndroidStudio's tutorial(https://developer.android.com/training/basics/firstapp).

NOTE: To make the app work, you need to mask the installation process from Android's default installer (which requires ROOT and recompile the installer) and use Intent to pass the application information to the app to be installed.




