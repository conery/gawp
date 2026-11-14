# Define a Workflow with Plugins

GAWP is organized as a set of **plugin modules** that carry out individual steps of the full linaerization workflow.

| Plugin Name | Module Name | Resonsibilities |
| -- | -- | -- |
| IO | `gawp.io` | Opens spreadsheets, extracts data from sheets |
| Geometry | `gawp.geometry` | Computes distances between points and line segments |
| Foci | `gawp.geometry.foci` | Reads positions of foci |
| Measurements | `gawp.geometry.measurements` | Reads measurement points, uses them to create line segments |
| Join | `gawp.join` | Copies data from Volume, Sphericity, and other sheets |
| Group | `gawp.group` | Summarizes Intensity data to create counts |
| Stages | `gawp.stages` | Assigns meiotic stage names to foci |

Each application decides which of these plugins to install.
A minimal workflow might use only Geometry, Foci, and Join in order to create a table that has positions of cells and their attributes, skipping the linearization step.
At the other extreme, a project can use all of the plugins to implement the full linearization pipeline.

This Overview section has short descriptions of each plugin and examples of workflows that use them.
Complete details are in the Plugins section.
