# Church Seating Optimization Program

### Overview
This program finds an "optimal" seating arrangement for a given available pew seating capacity on a first-come-first-serve basis (order of reservation).
When the Submit button is clicked, on success, a CSV file will be downloaded with each family/group's information and their seat assignments.

It was initially designed for the Newman Center Catholic Community at UCSD parish to assist in the re-opening process, after having closed the church as a result of the CoVid-19 pandemic.

### Host
https://church-seating-optimization.herokuapp.com/

### Inputs
This program takes in a number of inputs:
  - Family Reservations File (.csv) - earliest families at the top
  - Church's Available Pew Seating (.csv)
  - Max Capacity for entire church (including presiders, choir members, etc.)
  - Number of Reserved Seating (Presiders, choir members, ministers, etc.)
  - Distance of Separation (in feet)
  - Width of a single seat in a pew (in inches)

CSV File Format
----
### Available Pew Seating CSV File Example
| Section | Row # | Capacity |
| :----: | :----:  |  :----: |
| A | 2 | 10 |

### Family/Group Reservations CSV File Example
| First Name | Last Name | Group Size | E-mail Address |
|---	|---	|---	|---	|
| David | Tu | 4 | example@gmail.com |

### Output File
The columns shown are used by the Newman Center at UCSD. You may choose not to use them.
| First Name | Last Name | Group Size | E-mail Address | Door | Section | Row # | Seats |
|---	|---	|:---:	|---	|:---:	|:---:	|:---:	|---	|
| David | Tu | 4 | example@gmail.com | A | A | 2 | [1,2,3,4]

The door number corresponds to the section, representing the specific door to go through to get to that section. Seat numbers are numbered from right to left per pew. The row numbers start from 1. The door/section and row #s come from the input CSV – they do not have to be numbers.
