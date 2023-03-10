gcloiu# Integration 

Python project to replicate and expand the capabilities of the existing integration platform.


## Getting Started



### Prerequisites

Set up as a developer.  You'll need to have some stuff on your local machine.  
Always add items to the windows path when asked.

```
Git:    Download and install Git ->
        https://git-scm.com/downloads
        ***Pick defaults for the install process that are best aligned 
           for Python and Windows.
           
Python: Download and install Python. Currently using v3.7.2
        https://www.python.org/downloads/
        
        Or use pyenv to easily manage Python versions:
         - https://github.com/pyenv/pyenv/ (for UNIX or macOS)
         - https://github.com/pyenv-win/pyenv-win (for Windows)
        
IDE:    Pycharm Community will do the trick-> 
        https://www.jetbrains.com/pycharm/download/#section=windows   

MongoDB  
SQLServer
```

### Installing

* On windows machine, ensure Python is on the path.  
* Use Pip to install packages -> [How to use pip](https://packaging.python.org/tutorials/installing-packages/) 
    


## Running the tests

No automated Tests at this time... Testing TBD

## Deployment
TBD

## Built With
* [python 3.7.2](https://www.python.org/downloads/) -Base Scripting Language
* [Flask](https://flask.palletsprojects.com/en/1.0.x/quickstart/) - WSGI Application Framework
* [Flask-Bootstrap]( https://pythonhosted.org/Flask-Bootstrap/) - Extension for Bootstrap 4 (Js)
* [requests](http://docs.python-requests.org/en/master/user/install/) --Simple Http HTTP library

## Contributing

For collaboration, stick to the Git-flow branching model by using these branches:

* `master` - the main branch where the source code of HEAD always reflects a production-ready state.
* `experimental` - the main branch where the source code of HEAD always reflects a state with the latest delivered
  development changes for the next release
* `feature/[<targetprocess_id>-]<descriptive_name>` - as feature branches branched off from `experimental`, with
  (if applicable) the numerical ID of the related ticket in Targetprocess, and a human-readable name,
  connected-by-dashes.
* `release` - For (versioned) releases.

Apart from this, and versioning, there are no further standards at this time. If you are on the IJIT team, you may
contribute to a branch.


## Versioning

Versioning will be according to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
with a list of notable changes in the [CHANGELOG](CHANGELOG.md) file.


## Authors

* **Nicholas Straw** - *Initial setup and Continuous Development* - IJIT-Integration
* **Adil Yakubov** - *Continuous Development* - IJIT-Integration
* **Edwin VDT** - *Dev/Ops Engineer* - IJIT-Dev/Ops

## License


## Notes

* Internal app servicing IT and super user customers

