using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Data;
using Mono.Data.Sqlite;
using System;

public class PaintingsDB : Singleton<PaintingsDB>
{

    IDbConnection dbcon;
    IDataReader reader;
    IDbCommand cmnd_read;

    private void openDBConnectionAndCreateCommand()
    {
        // Application.streamingAssetsPath for jar:file
        // https://stackoverflow.com/questions/50753569/setup-database-sqlite-for-unity

        string nameOfDB = "/PaintingsSourceLinkInfo.db"; //StreamingAssets
        string uriPrefix = "URI=file:";

        string persistentDataPath = uriPrefix + Application.persistentDataPath + nameOfDB;
        //Debug.Log("Application.persistentDataPath: " + persistentDataPath);

        string streamingAssetsPath = uriPrefix + Application.streamingAssetsPath + nameOfDB;
        //Debug.Log("Application.streamingAssetsPath: " + nameOfDB);

        string dataPath = uriPrefix + Application.dataPath + nameOfDB;
        //Debug.Log("Application.dataPath: " + dataPath);

        dbcon = Application.platform == RuntimePlatform.Android ? 
            new SqliteConnection(Application.persistentDataPath + nameOfDB) : 
            new SqliteConnection(streamingAssetsPath);

        dbcon.Open();
        cmnd_read = dbcon.CreateCommand();
    }

    private void printReaderContent()
    {
        for(int i = 0; i < reader.FieldCount; i++)
        {
            Debug.Log(i + ": " + reader[i]);
        }
        
    }

    public void readGetUniqueValuesByColumn(string columnName)
    {
        ArrayList values = getUniqueValuesByColumn(columnName);

        foreach (var item in values)
            Debug.Log(item.ToString());
    }

    public ArrayList getUniqueValuesByColumn(string columnname)
    {
        openDBConnectionAndCreateCommand();

        var valueList = new ArrayList();

        string query = "SELECT DISTINCT " + columnname + " FROM paintings_info ORDER BY " + columnname + " COLLATE NOCASE ASC";
        cmnd_read.CommandText = query;
        reader = cmnd_read.ExecuteReader();

        while (reader.Read())
        {
            valueList.Add(reader[0].ToString());
        }

        dbcon.Close();
        valueList.Sort();
        return valueList;
    }

    public List<GameObject> getPanelPaintingListFromColumname(GameObject preFab, string columnname, string rowValue, bool like, bool any)
    {
        if (rowValue.Length >= 3 && !rowValue.StartsWith(" "))
        {
            openDBConnectionAndCreateCommand();
            //string query = "SELECT * FROM paintings_info WHERE " + columnname + " = " + rowValue;
            string query = "";
            //string query = like ? "SELECT * FROM paintings_info WHERE " + columnname + " like '%" + rowValue + "'" :
            //  "SELECT * FROM paintings_info WHERE " + columnname + " = '" + rowValue + "'";

            rowValue = NGACalculationHelper.FixStringForSQL(rowValue);

            if (like)
            {
                if (any)
                {
                    query = "SELECT * FROM paintings_info WHERE " + columnname + " like '%" + rowValue + "%'";
                }
                else
                {
                    query = "SELECT * FROM paintings_info WHERE " + columnname + " like '" + rowValue + "%'";
                }
                 
            }
            else
            {
                query = "SELECT * FROM paintings_info WHERE " + columnname + " = '" + rowValue + "'";
            }

            //string query = "SELECT * FROM paintings_info WHERE " + columnname + " like '%"+ rowValue + "'";
            //string query = "SELECT * FROM paintings_info WHERE " + columnname + " = '" + rowValue + "'";

            Debug.Log("Full query: " + query);

            //Debug.Log(query);
            cmnd_read.CommandText = query;
            reader = cmnd_read.ExecuteReader();
            //reader.Read();

            var panelPaintingGameObjectList = new List<GameObject>();

            while (reader.Read())
            {
                // Create object from prefap

                // Create obj for each paintingObj
                GameObject gameO = Instantiate(preFab, new Vector3(0, 0, 0), Quaternion.identity);

                // panelPaintingGameObjectList.Add(

                // Add Painting component to each Painting
                gameO.AddComponent<Painting>();

                // Get texture added to the Painting component
                setPaintingFromReader(gameO.GetComponent<Painting>(), reader).ToString();

                panelPaintingGameObjectList.Add(gameO);
                // gameO.GetComponent<Painting>().PanelPaintingGameObject = gameO; // not important
            }

            dbcon.Close();
            return panelPaintingGameObjectList;

        }

        return null;
    }

        // var dataType = reader.GetFieldType(index);
        // if (dataType == typeof(String))

        private long getReaderValueInt(int index, IDataReader reader)
        {
            if (reader.FieldCount - 1 >= index)
            {
            Type dataType = reader.GetFieldType(index);
                if(dataType == typeof(long))
                {
                return reader.GetInt64(index);
                }else if(dataType == typeof(string))
            {
                try
                {
                    return Int64.Parse(reader[index].ToString());
                }
                catch (FormatException)
                {
                    Console.WriteLine($"Unable to parse '{index}'");
                }
            }
            }
        Debug.LogWarning("Reader could not find Long in " + index + "\n" +
            "reader.FieldCount = " + reader.FieldCount);
        return 0;
        }

    private string getReaderValueString(int index, IDataReader reader)
    {
        if (reader.FieldCount - 1 >= index)
        {
            Type dataType = reader.GetFieldType(index);
            
            if (dataType == typeof(string))
            {
                return reader[index].ToString();
            }
            else if (dataType == typeof(long))
            {
                try
                {
                    Debug.LogWarning("Long was found instead of String");
                    return reader[index].ToString();
                }
                catch (FormatException)
                {
                    Console.WriteLine($"Unable to parse '{index}'");
                    return "";
                }
            }
        }
        Debug.Log(reader.GetFieldType(index));
        Debug.LogWarning("Reader could not find String in " + index + "\n" +
                   "reader.FieldCount = " + reader.FieldCount);
        return "";
    }

        public Painting setPaintingFromReader(Painting painting, IDataReader reader)
    {
        painting.Objectid = getReaderValueInt(0, reader);
        painting.Title = getReaderValueString(1, reader);
        painting.Attribution = getReaderValueString(2, reader);
        painting.Beginyear = getReaderValueInt(3, reader);
        painting.Endyear = getReaderValueInt(4, reader);
        painting.Displaydate = getReaderValueString(5, reader);
        painting.Classification = getReaderValueString(6, reader);
        painting.Medium = getReaderValueString(7, reader);
        painting.Width = getReaderValueInt(8, reader);
        painting.Height = getReaderValueInt(9, reader);
        painting.Iiifurl = getReaderValueString(10, reader);

        painting.GenerateInfo();

        return painting;

        //painting.setPainting(reader.GetInt64(0), "" + reader[1].ToString(), "" + reader[2].ToString(), reader.GetInt64(3), reader.GetInt64(4),
        //         "" + reader[5].ToString(), "" + reader[6].ToString(), "" + reader[7].ToString(), reader.GetInt64(8), reader.GetInt64(9), "" + reader[10].ToString());

        /*
        if (reader.FieldCount == 11)
        {
            painting.setPainting(reader.GetInt64(0), "" + reader[1].ToString(), "" + reader[2].ToString(), reader.GetInt64(3), reader.GetInt64(4),
                    "" + reader[5].ToString(), "" + reader[6].ToString(), "" + reader[7].ToString(), reader.GetInt64(8), reader.GetInt64(9), "" + reader[10].ToString());
        }
        else
        {
            painting.setPainting(reader.GetInt64(0), "" + reader[1].ToString(), "" + reader[2].ToString(), reader.GetInt64(3), 0,
                    "", "" + "", "" + "", 0, 0, "" + "");
        }*/
    }

    public string getAttributionFromReader(IDataReader reader)
    {
        return reader[2].ToString();
    }
}
