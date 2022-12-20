## Create deployment artifacts

# folder python is one of the default search paths for libraries
if(Test-Path -Path python) {
    rm -r python/*
} 

python -m pip install -r requirements.txt -t python/

if(Test-Path -Path library.zip -PathType Leaf) {
    rm library.zip
} 

zip -r library.zip python/