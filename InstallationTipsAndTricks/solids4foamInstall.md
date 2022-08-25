# Installing solids4foam natively

## Creating FOAM_RUN (just in case of not having this directory)

The repository can be placed anywhere, but I am assuming that is better to follow the steps from a Phillip Cardiff presentation.

```
mkdir -p $FOAM_RUN
```

## Cloning the repository

```
cd $FOAM_RUN

git clone https://bitbucket.org/philip_cardiff/solids4foam-release.git
```

## Compiling

Currently, you can compile solid4Foam in foam-extend-4.0, foam-extend-4.1, OpenFOAM-v1812, OpenFOAM-v1912, OpenFOAM-7. foam-extend-4.0 is recommended, but I see more advantages using foam-extend-4.1 with csvFile reading option.

```
cd solids4foam-release

./Allwmake
```

## Replacing files in OpenFOAM-v1912

If you try to compile solids4Foam with v1912 you are going to be asked to replace some files. Do what they say in the error log:

```
cp filesToReplaceInOF/AMIInterpolation.C /home/<user>/OpenFOAM/OpenFOAM-v1912/src/meshTools/AMIInterpolation/AMIInterpolation/

cp filesToReplaceInOF/AMIInterpolation.H /home/<user>/OpenFOAM/OpenFOAM-v1912/src/meshTools/AMIInterpolation/AMIInterpolation/

wmake libso /home/<user>/OpenFOAM/OpenFOAM-v1912/src/meshTools
```

obs: Compiling OpenFOAM-v1912 in your home can make your life easier since you need to substitute and compile code later.
