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

