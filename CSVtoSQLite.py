# import libraries
import os
import pandas
import sqlite3
import dask.dataframe as dd


def main():
    print("Welcome to CSVtoSQLite!")
    print("This program will convert all CSV files in a folder into SQLite databases.")
    print("folderPath: Enter the path to the folder containing the CSV log files. ")
    inputFolder = inputFolderPath()
    print("exportFolder: The path to the folder where the SQLite databases will be exported. ")
    exportFolder = exportFolderPath()
    print("The name of the SQLite database. ")
    dbName = databaseName()
    csvToSqlite(inputFolder, exportFolder, dbName)


def inputFolderPath():
    input_folder = input("Enter folder path: ")
    try:
        if os.path.isdir(input_folder):
            return input_folder
        else:
            print("Unable to locate folder. Please try again.")
            return inputFolderPath()
    except:
        # recursive call if an exception occurs
        print("Invalid path. Please try again.")
        return inputFolderPath()


def exportFolderPath():
    exportFolder = input("Enter folder path: ")
    try:
        if os.path.isdir(exportFolder):
            return exportFolder
        else:
            print("Unable to locate folder. Please try again.")
            return exportFolderPath()
    except:
        # recursive call if an exception occurs
        print("Invalid path. Please try again.")
        return exportFolderPath()


def databaseName():
    try:
        databaseName = input("Enter database name: ")
        return databaseName
    except:
        print("Invalid database name. Please try again.")
        return databaseName()


def csvToSqlite(folderPath, dbFolderPath, databaseName):
    # specify SQLite database path, file name, and extension
    dbPath = os.path.join(dbFolderPath, databaseName + '.db')
    dbConnection = sqlite3.connect(dbPath)
    cursor = dbConnection.cursor()
    # Create a table to store the CSV data
    for filename in os.listdir(folderPath):
        if filename.endswith('.csv'):
            print(f"Processing {filename}...")
            # Read CSV file into Dask DataFrame
            filePath = os.path.join(folderPath, filename)
            ddf = dd.read_csv(filePath)
            # Remove duplicates that exist within the first row
            firstRow = ddf.head(1)
            ddf = ddf.drop_duplicates(subset=firstRow.columns.tolist())
            # Get table name from CSV file name (without extension)
            tableName = os.path.splitext(filename)[0]
            # Replace spaces with underscores
            tableName = tableName.replace(' ', '_')
            # Convert Dask DataFrame back to Pandas DataFrame and write to SQL
            ddf.to_sql(tableName, dbConnection,
                       if_exists='replace', index=False, compute=True)

    # Close the SQLite connection
    dbConnection.close()
    print("Done, exiting")


if __name__ == "__main__":
    main()
