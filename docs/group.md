# Group

## Counting Spots

The Group stage summarizes the data in one of the sheets to produce counts.
The process is best explained using a sheet from one of the example data sets.

A sheet named "Intensity Max Ch=4 Img=1" has a table that connects spots to surfaces.
This is what the sheet looks like in Excel:

<img src="../images/group_sheet.png" style="zoom:100%" />

There are two parts to the table. 
The upper part has the word "Surface" in the Category column, and the lower part (shaded in green) has "Spot" in that column.

The essential thing to know about this table is that unlike most other sheets, the leftmost column, labeled "Intensity Max", does not actually contain intensity values.
Those numbers are IDs.
For the surface rows IDs are numbers ranging from 1 to 53, which is the number of surfaces in the data set.

For the spots, the number in the left column is the ID of the surface that (according to Imaris) the spot is closest to.
Most spots have a 0 in this column, which means the spot is not associated with any surface.
But you can see at the bottom of the figure, in row 5283, there is a 10 in the leftmost column, which means this spot is closest to surface number 10.
Other spots below that have 9, 10, or 11 in the leftmost column, meaning they are close to surfaces with those IDs.

### Algorithm

The Group stage gets its name from `groupby`, another concept borrowed from relational databases and widely used in Pandas and other data science libraries.
The main steps in this plugin are:

1. Split the sheet into two parts and make two data frames, one for surfaces and one for spots

1. Group the spots according to their IDs, and count the number of rows in each group; note that the name of each group is the ID of one of the surfaces

1. Append the counts to the end of the surfaces frame using a join operation that connects counts to surfaces using the ID column

Here is what the group operation looks like:

<img src="../images/group_count.png" style="zoom:100%" />

Note that the first row is the count of the number of spots that have 0 in the "Intensity Max" column.
This count is ignored when the counts are joined with the surfaces.

The result of that join is shown below.
The yellow shading highlights the fact that the join is using the column named "Intensity Max" and that this column appears in both the spots and surfaces frames.

<img src="../images/group_final.png" style="zoom:100%" />

## Plugin Configuration

The configuration section that adds a Group plugin should have a name consisting of the word "group", a period, and a name.
Within each section define the attributes to use for that plugin:

| Attribute | Default | Note |
| -- | -- | -- |
| `sheet` | (required) | name of the sheet with data to join |
| `column` | (required) | column that contains the data to copy |
| `category_column` | `''` | column for filtering rows |
| `category` | `''` | value for filtering rows |
| `group` |  (required) | the value for rows to group by |
| `aggregation_function` |  `count` | |
| `aggregation_name` |  (required) | name for the output column |
| `index` | `''` | names of columns for creating IDs |

If the `category_column`, `category`, or `index` attributes are left out they are copied from the Geometry plugin.

#### Example

This is the configuration section that was used for the example data shown above:

```
[group.intensity]
sheet = 'Intensity Max Ch=4 Img=1'
category_column = 'Category'
category = 'Surface'
group = 'Spot'
column = 'Intensity Max'
aggregation_function = 'count'
aggregation_name = 'RAD51'
```

<img src="../images/group.png" style="zoom:100%" />

## API

The Group plugins are accessed via the [Plugin Manager](manager.md).

`plugins.group`

:   A reference to the top level Group plugin, which maintains a list of objects, one for each group to create.

`plugins.group.sheets`

:   A list of GroupSheet objects, each of which has specifications for grouping one column.

`plugins.join.grouped_frame`

:   A Pandas DataFrame created by the `apply` method.  It has one column for each group created.

#### Methods

`plugins.group.apply()`

:   Iterates over all sheets, extracting the data, forming groups, and saving them in the output frame.
