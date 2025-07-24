# import libraries
import os
import pandas
import sqlite3
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


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

    # Connect to SQLite database (or create it)
    conn = sqlite3.connect(dbPath)
    cursor = conn.cursor()

    # Define the number of chunks and cores
    chunk_size = 10000
    num_cores = os.cpu_count()

    # Iterate through all CSV files in the folder
    for filename in os.listdir(folderPath):
        if filename.endswith('.csv'):
            print(f"Processing {filename}...")
            # Read CSV file into DataFrame
            filePath = os.path.join(folderPath, filename)

            # Function to process each chunk
            def process_chunk(chunk):
                # Remove duplicates that exist within the first row
                firstRow = chunk.iloc[0]
                return chunk.drop_duplicates(subset=firstRow.index.tolist())

            # Use ProcessPoolExecutor to process chunks in parallel
            with ProcessPoolExecutor(max_workers=num_cores) as executor:
                # Read in chunks and process them
                chunks = pandas.read_csv(
                    filePath, chunksize=chunk_size, low_memory=False)
                processed_chunks = list(executor.map(process_chunk, chunks))

            # Concatenate results back to a DataFrame
            df = pandas.concat(processed_chunks)

            # Get table name from CSV file name (without extension)
            tableName = os.path.splitext(filename)[0]
            # Replace spaces with underscores
            tableName = tableName.replace(' ', '_')

            # Write DataFrame to SQLite table using 'replace' mode
            df.to_sql(tableName, conn, if_exists='replace', index=False)

    # Close the SQLite connection
    conn.close()
    print("Done, exiting")


if __name__ == "__main__":
    main()
