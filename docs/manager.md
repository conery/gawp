# Plugin Manager

The Plugin Manager is a module that keeps track of which plugins have been installed for an application.

GAWP defines a global variable named `plugins` that can be accessed by all of the modules in GAWP and by applications.
As the `initialize_config` function creates plugins they are registered with the plugin manager, where they become accessible as attributes of the `plugins` object.

All of the attributes are initially set to `None`.
An application can check to see if a plugin was installed by testing the value of an attribute, _e.g._

```
if plugins.join is not None:
    # do something with joins
```

| Attribute | Plugin | Notes |
| -- | -- | -- |
| `plugins.io` | IO | required by command line applications|
| `plugins.geometry` | Geometry | |
| `plugins.geometry.foci` | Foci | |
| `plugins.geometry.measurements` | Measurements | |
| `plugins.join` | Join | a list of JoinSheet objects |
| `plugins.group` | Group | a list of GroupSheet objects |
| `plugins.stages` | Stages | |

