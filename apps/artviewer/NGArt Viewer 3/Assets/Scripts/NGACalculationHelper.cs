using UnityEngine;

public class NGACalculationHelper
{

    private static string replaceChars(string stringToFix, string notAllowedChar)
    {
        return stringToFix.Replace(notAllowedChar, @"\'" + notAllowedChar);
    }

    public static string FixStringForSQL(string stringToFix)
    {
        //stringToFix = replaceChars(stringToFix, "'");
        //stringToFix = replaceChars(stringToFix, @"\");

        Debug.Log(stringToFix);
        stringToFix = stringToFix.Replace(@"\", @"\\");
        stringToFix = stringToFix.Replace("'", "''");
        Debug.Log(stringToFix);

        /*
        stringToFix = replaceChars(stringToFix, "&");
        stringToFix = replaceChars(stringToFix, "*");
        stringToFix = replaceChars(stringToFix, "@");
        stringToFix = replaceChars(stringToFix, "[");
        stringToFix = replaceChars(stringToFix, "]");
        stringToFix = replaceChars(stringToFix, "{");
        stringToFix = replaceChars(stringToFix, "}");

        stringToFix = replaceChars(stringToFix, "^");
        stringToFix = replaceChars(stringToFix, ":");
        stringToFix = replaceChars(stringToFix, "=");
        stringToFix = replaceChars(stringToFix, "!");
        stringToFix = replaceChars(stringToFix, "/");
        stringToFix = replaceChars(stringToFix, ">");
        stringToFix = replaceChars(stringToFix, "-");
        stringToFix = replaceChars(stringToFix, "(");
        stringToFix = replaceChars(stringToFix, ")");
        stringToFix = replaceChars(stringToFix, "%");
        stringToFix = replaceChars(stringToFix, "+");
        stringToFix = replaceChars(stringToFix, "?");
        stringToFix = replaceChars(stringToFix, ";");
        stringToFix = replaceChars(stringToFix, "~");
        stringToFix = replaceChars(stringToFix, "|");
        */

        return stringToFix;

    }
        public static string TranslateDropdownSearchColumnName(string inputString)
        {

           // Debug.Log("Inputmode: " + inputString);

            if (inputString == "Search: Artist")
            {
                return "attribution";
            }
            else if (inputString == "Search: Title")
            {
                return "title";
            }
            else if (inputString == "Search: Year")
            {
                return "endyear";
            }

            return "title";
        }

        public static void IsGameObjectNull(GameObject gO)
        {
            if (gO == null)
            {
                Debug.LogWarning(gO.name + " is null!");
            }
        }

    public static string ConcatStringTo50(string toConcat)
    {
        if (toConcat.Length > 60)
        {
            toConcat = toConcat.Substring(0, 60);
        }

        return toConcat;
    }
}
