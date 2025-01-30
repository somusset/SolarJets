These are further details on how to install the requirements when using Windows. Note that this is done with Anaconda installed on the machine.

### Visual studio
Visual studio tools have to be installed.
- Download Build tools from this website: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Install the Visual Studio 2022 Build Tools
- Select the Universal Windows App package and on the right side, select the "C++ (v143)" like below

### Git
Git needs to be installed:
```bash
conda install -c anaconda git
```

### Python version
It is recommended to use a conda environment with a specific Python version (it should work with versions between 3.9 and 3.11 but in practice this has been tested with 3.9) to avoid any problems down the road when installing the different required packages.
```bash
conda create --name aggregationenv python=3.9
```

### Package installation
Packages must be installed in the following order to avoid conflicts:

```bash
pip install panoptescli
pip install python-magic python-magic-bin
```
Then this repository is downloaded, and we switch to the `fem` branch
```bash
git clone https://github.com/ramanakumars/SolarJets.git
cd SolarJets
git reset --hard remotes/origin/fem
cd ..
```
Then we install the aggregation package provided by Zooniverse:
```bash
pip install -U git+https://github.com/zooniverse/aggregation-for-caesar.git
```
Then we continue by installing the packages required by our pipeline
```bash
cd SolarJets
python -m pip install -r requirements.txt
```

To test if panoptes has been properly installed, we can try:
```bash
panoptes --help
```
A help text should be displayed.
