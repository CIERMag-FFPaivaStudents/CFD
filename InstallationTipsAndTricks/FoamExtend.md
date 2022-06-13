# FOAM-Extend 4.0 for Ubuntu 20.04

Before the installation you should check your Bison version (2.x in FOAM-Extend 4.0 or 3.x in FOAM-Extend 4.1)

## Make directory and clone repository

It is important to set the installation directory in your $HOME to assure permissions.

```
mkdir ~/foam
cd ~/foam
git clone git://git.code.sf.net/p/foam-extend/foam-extend-4.0 foam-extend-4.0
```

## Install dependencies

Add repositories and install libraries.

```
echo "deb http://archive.ubuntu.com/ubuntu xenial main" | sudo tee /etc/apt/sources.list.d/xenial.list


sudo add-apt-repository ppa:rock-core/qt4
sudo apt-get update


sudo apt-get install git-core build-essential binutils-dev cmake flex \
zlib1g-dev qt4-dev-tools libqt4-dev libncurses5-dev \
libxt-dev rpm mercurial graphviz python python-dev  gcc-5 g++-5
```

## Set environment variables

```
cd ~/foam/foam-extend-4.0
source etc/bashrc
echo "alias fe40='source \$HOME/foam/foam-extend-4.0/etc/bashrc'" >> $HOME/.bashrc
```

## DON'T FORGET THIS STEP BEFORE THE INSTALL COMMAND

```
sed -i -e 's=rpmbuild --define=rpmbuild --define "_build_id_links none" --define=' ThirdParty/tools/makeThirdPartyFunctionsForRPM
sed -i -e 's/gcc/\$(WM_CC)/' wmake/rules/linux64Gcc/c
sed -i -e 's/g++/\$(WM_CXX)/' wmake/rules/linux64Gcc/c++
```

## Install FOAM-Extend

```
./Allwmake.firstInstall
```

## (Optional) Get fsiFOAM and install 
If you have the intent of using fsiFOAM with primitive functions such as csvFile, you should consider installing FOAM-Extend 4.1 (such functionalities were implemented by Henrik Rusche in this newer version).

```
wget https://openfoamwiki.net/images/d/d6/Fsi_40.tar.gz
tar -xzf Fsi_40.tar.gz

cd FluidSolidInteraction/src
./Allwmake
```

### Fix dependencies

```
cd ..
find run -name options | while read item
do
sed -i -e 's=$(HOME)/foam/foam-extend-4.0/applications/solvers/FSI=$(HOME)/foam/foam-extend-4.0)/FluidSolidInteraction/src=' $item
sed -i -e 's=$(HOME)/foam/foam-extend-4.0/packages/eigen3=$(HOME)/foam/foam-extend-4.0/
FluidSolidInteraction/src/ThirdParty/eigen3=' $item
done
```

### Fix bugs
First you need to UNCOMMENT lines (382-394) from foam-extend-4.0/src/finiteVolume/finiteVolume/fvSchemes/fvSchemes.C 

```
         if (dict.found("fluxRequired"))
         {
             fluxRequired_ = dict.subDict("fluxRequired");

             if
             (
                 fluxRequired_.found("default")
              && word(fluxRequired_.lookup("default")) != "none"
             )
             {
                 defaultFluxRequired_ = Switch(fluxRequired_.lookup("default"));
             }
         }
```

Now you need to COMMENT lines (1044-1051 in fe40 or 1133-1140 in fe41) from foam-extend-4.0/src/finiteVolume/fvMatrices/fvMatrix/fvMatrix.C

```
    //if (!psi_.mesh().schemesDict().fluxRequired(psi_.name()))
    //{
    //    FatalErrorIn("fvMatrix<Type>::flux()")
    //        << "flux requested but " << psi_.name()
    //        << " not specified in the fluxRequired sub-dictionary"
    //           " of fvSchemes."
    //        << abort(FatalError);
    //}
```

Finally, compile the code changes:

```
cd $HOME/foam/foam-extend-4.0/src/finiteVolume
wmake libso
```




