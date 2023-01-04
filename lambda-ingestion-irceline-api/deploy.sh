## Create deployment artifacts

# folder python is one of the default search paths for libraries
if(Test-Path -Path python) {
    rm -r python/*
} 

python -m pip install `
    --platform manylinux2014_x86_64 `
    --implementation cp `
    --python 3.8 `
    --only-binary=:all: `
    --upgrade `
    -r requirements.txt `
    -t python/
    
if(Test-Path -Path library.zip -PathType Leaf) {
    rm library.zip
} 

zip -r library.zip python/

$artifact="irceline-lambda-packages-layer.zip" 
$awsbucket="deployment-artifacts-jonas"

aws s3api put-object --bucket $awsbucket --key $artifact --body library.zip