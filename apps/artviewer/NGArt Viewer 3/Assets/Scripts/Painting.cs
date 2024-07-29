using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class Painting : MonoBehaviour
{
    
    private long objectid = 0;
    private string title = "Missing";
    private string attribution = "Missing";
    private long beginyear = 0;
    private long endyear = 0;
    private string displaydate = "Missing";
    private string classification = "Missing";
    private string medium = "Missing";
    private long width = 0;
    private long height = 0;
    private string iiifurl = "Missing";
    private string fullURL = "Missing";
    private string fullURLdownsized = "Missing";
    private string fullURLthumb = "Missing";

    private Texture2D texture2DThumb;
    private Texture2D texture2D;
    private Texture2D texture2DFullSize;

    private Image imageGameObject;
    private TextMeshProUGUI textMeshProUGUI;

    private GameObject panelPaintingGameObjectFromPrefab;

    public long Objectid { get => objectid; set => objectid = value; }
    public string Title { get => title; set => title = value; }
    public string Attribution { get => attribution; set => attribution = value; }
    public long Beginyear { get => beginyear; set => beginyear = value; }
    public long Endyear { get => endyear; set => endyear = value; }
    public string Displaydate { get => displaydate; set => displaydate = value; }
    public string Classification { get => classification; set => classification = value; }
    public string Medium { get => medium; set => medium = value; }
    public long Width { get => width; set => width = value; }
    public long Height { get => height; set => height = value; }
    public string Iiifurl { get => iiifurl; set => iiifurl = value; }
    public string FullURL { get => fullURL; set => fullURL = value; }
    public string FullURLdownsized { get => fullURLdownsized; set => fullURLdownsized = value; }
    public string FullURLthumb { get => fullURLthumb; set => fullURLthumb = value; }
    public Texture2D Texture2DThumb { get => texture2DThumb; set => texture2DThumb = value; }
    public Texture2D Texture2D { get => texture2D; set => texture2D = value; }
    public Texture2D Texture2DFullSize { get => texture2DFullSize; set => texture2DFullSize = value; }
    public Image ImageGameObject { get => imageGameObject; set => imageGameObject = value; }
    public TextMeshProUGUI TextMeshProUGUI { get => textMeshProUGUI; set => textMeshProUGUI = value; }
    public GameObject PanelPaintingGameObjectFromPrefab { get => panelPaintingGameObjectFromPrefab; set => panelPaintingGameObjectFromPrefab = value; }

    public void GenerateInfo()
    {

        if(Width > 4096 || Height > 4096)
        {

            if (Width > 4096)
            {
                Width = 4096;
            }

            if (Height > 4096)
            {
                Height = 4096;
            }

            this.FullURL = this.Iiifurl + "/full/!" + Width + "," + Height + "/0/default.jpg";
        }
        else
        {
            this.FullURL = this.Iiifurl + "/full/" + Width + "," + Height + "/0/default.jpg";
        }

        if (this.Height > 1500 || this.Width > 1500)
        {
            this.FullURLdownsized = this.Iiifurl + "/full/!" + 1500 + "," + 1500 + "/0/default.jpg";
        }
        else
        {
            this.FullURLdownsized = this.Iiifurl + "/full/!" + Width + "," + Height + "/0/default.jpg";
        }

        /*
        if (this.Height1 > 1500 || this.Width1 > 1500)
        {
            int height2 = 1500;
            this.FullURLdownsized = this.Iiifurl1 + "/full/!" + height2 + "," + height2 + "/0/default.jpg";
        }
        else
        {
            this.FullURLdownsized = this.Iiifurl1 + "/full/!" + width + "," + height + "/0/default.jpg";
        }*/


        this.FullURLthumb = this.Iiifurl + "/full/!200,200/0/default.jpg";
    }

    public override string ToString()
    {
       return "objectid = " + Objectid + " | " +
"title = " + Title + " | " +
"attribution = " + Attribution + " | " +
"beginyear = " + Beginyear + " | " +
"endyear = " + Endyear + " | " +
"displaydate = " + Displaydate + " | " +
"classification = " + Classification + " | " +
"medium = " + Medium + " | " +
"width = " + Width + " | " +
"height = " + Height + " | " +
"iiifurl = " + Iiifurl + " | " +
"fullURL = " + FullURL + " | ";
    }


}
