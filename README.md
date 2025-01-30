# SolarJets
Tools and scripts for working with the SolarJets zooniverse project.   

In this README file we go through the workflow of this package, specifically the order in which the aggregation in run. The ipynb notebooks contained in this directory are listed with their primary function and when they can be usefull to open. 

# Installation
## Requirements
To install the required python modules, run the following in main repo folder:
```bash
python3 -m pip install -r requirements.txt
```
### Windows users
Some more steps might be needed, as described [here](Installation_windows.md).

## One-time panoptes-cli configuration
You need to configure the panoptes client with your Zooniverse username and password:
```bash
panoptes configure
```
This is done only the first time, right after the installation.

# Usage
## Download data
Before doing the aggregation, one needs to download some data from the Zooniverse project. In these instructions we use the panotpes client but in principle these files can be downloaded directly from the project lab website.

We need the workflows report
```bash 
panoptes project download -t workflows 11265 solar-jet-hunter-workflows.csv
```
The JetOrNot classifications report, in the `/JetOrNot` directory
```bash
cd JetOrNot
panoptes workflow download-classifications 25059 jet-or-not-classifications.csv
```
The BoxTheJet classifications report, in the `/BoxTheJets` directory
```bash
cd ../BoxTheJets
panoptes workflow download-classifications 21225 box-the-jets-classifications.csv
```

## Generate the configuration files
### Generation of the files using panoptes
If configuration files are not present in the `/configs` directory, then they need to be created, for each of the workflows:
```bash
cd ../configs
panoptes_aggregation config solar-jet-hunter-workflows.csv 25059
panoptes_aggregation config solar-jet-hunter-workflows.csv 21225
```
This will create, for each workflow, an extractor configuration file, a reducer configuration file, and a task labels file.

### Modifications to the configuration files

Recommended change in `Extractor_config_workflow_25059_Vx.xx`:     
by default, the configuration file restricts the workflow version to a specific value. However any small change to the Zooniverse project might have triggered a change in version number, so it is recommended to change
```yaml
workflow_version: '2.15'
```
to
```yml
workflow_version: {'min': '2.15'}
```
(with the actual version number that you might want here).


## Aggregation



``` bash
# Start in the JetOrNot directory
cd JetOrNot
``` 

### Run the aggregation on the JetOrNot workflow results
Follow the steps in the README JetOrNot to do the aggregation steps of the data. 

### Check the results from the Jet or Not workflow by looking at ipynb notebooks
Look at the jet subject and non-jet subjects distribution over time.
`jet_time_distribution.ipynb`

Look at the resulting agreements and check the number of votes per subject.
`jetornot.ipynb`

Plot the agreement of the subjects in Jet Or Not workflow over time. Sorted by SOL/ HEK event
`Plotting_agreement_T0.ipynb`

### Go back to the main directory and into the BoxTheJet directroy
``` bash
cd ..
cd BoxTheJets/
```

### Run the aggregation on the BoxTheJets workflow results
Follow the steps in the README BoxTheJets to do the aggregation steps of the data.

### Check the results from the BoxTheJets workflow by looking at ipynb notebooks
Look at the first results of the jet aggregation. Check the resulting box and point clusters and the aggregation code in multiple jet subjects. 
`simple_analysis.ipynb`

Calculate the confidence of the jets found in the subjects. Are the jets of high quality or should a cut be made based on their confidence scores. 
`jet_confidence.ipynb`

Plot the agreement of the Jet Or Not question asked during the BoxThe Jets workflow, sorted by SOL/HEK event. Note that gaps will be present in the graphs due to the presence of only the pushed subjects. 
`Plotting_agreement_T3.ipynb`

From here you can also go on and export the Jet clusters from Find_export_jet_clusters.ipynb using the 'BoxTheJets/reductions/question_reducer_box_the_jets.csv' and for QuestionResult. However, since the question of the JetOrNot workflow and first question of the BoxTheJets workflow we can also combine the answers to get a better count on the agreement scores. 

### Go back to the main directory 
``` bash
cd ..
```

### Run the aggregation on the T0 and T3 files
``` bash
python3 make_reducer_combined.py
```

This combines the binary resulting of the first workflow and second workflow questions to make the combined answers. This creates the 'question_reducer_combined_workflows.csv' in the main directory.   

### Check the combined question results
Plot the agreement of the combined result of subjects over time. Sorted by SOL/ HEK event
`Plotting_agreement_Tc.ipynb`

Look at the results of the two workflow questions. Are the agreements scores changing during the second workflow? Do many subjects go from 'yes' to 'no' jet during the second worflow? Are the right subjects being send through?  
`Analysis_combined_question_results.ipynb`

### Exporting the Jet Clusters
Go back to the BoxTheJet/ folder
``` bash
cd BoxTheJets/
```
Open `Find_export_jetclusters.ipynb` and run the code until the end. Note that at the moment this part of the code can only be done on the foxsiadmins computer becaus access to the database is required. 
The export will be done in a json and a csv format. The csv format will be easier to quickly work with for the statistics, but for full access to the aggregated zooniverse data and the functions written for the JetCluster object the json file has a wider functionality. 

Look at the jet size evolution per SOL/HEK event
`Plotting_box_size.ipynb`

### Final results and analysis
Go back to main directory for the two last jupyter notebooks. 
``` bash
cd ..
```
Look at the extracted properties of the jet clusters. Get histograms of the length, width, duration, velocity, base position and uncertainty. Possibly filter data on a maximal uncertainty. Plot the jet location on the solar map. 
`Jet_statistics.ipynb`

Visualise the final Jet clusters, get the plots made during the aggregation per SOL/ HEK event and export the json or gif from one jet cluster. 
`Looking_jets_plots.ipynb`





