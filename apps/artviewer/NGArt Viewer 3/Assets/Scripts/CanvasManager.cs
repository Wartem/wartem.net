using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;
using UnityEngine.UI;
using TMPro;
using System.Net;
using System.IO;
using System;
using UnityEngine.EventSystems;

public class CanvasManager : Singleton<CanvasManager> , IPointerClickHandler
{

    GameObject contentContainer;

    GameObject mainPanel;
    GameObject mainPanelContent;

    GameObject paintingInfo;
    GameObject loadingText;
    Button downloadPainting;

    GameObject sidePanel;
    GameObject headerText;
    GameObject inputField;
    GameObject scrollView;
    GameObject viewport;
    GameObject content;

    GameObject InfoPanel;

    Button AppInformationButton;

    GameObject scrollbarVertical;

    GameObject suggestionDropDown;
    GameObject typeDropDown;
    GameObject classificationDropdown;

    Button thumbnailsDownloadButton;

    Button backButton;

    Button exitButton;

    List<string> allUniqueColumnAttribution;
    List<string> allUniqueColumnTitle;
    List<string> allUniqueColumnYearMadeIn;

    Webconnect webconnect;
    PaintingsDB paintingsDB;

    private TMP_InputField inputFieldComponent;

    RawImage rawImageMainPaintingPanel;
    Painting currentPainting;

    public GameObject panelPaintingPrefab;

    int minCharSearchCount = 4;

  

    //GameObject InputField

    // Start is called before the first frame update
    void Start()
    {

        // CanvasScaler.ScreenMatchMode.MatchWidthOrHeight

        webconnect = new Webconnect();
        paintingsDB = transform.GetComponent<PaintingsDB>();

        contentContainer = transform.Find("Content Container").gameObject;
        mainPanel = contentContainer.transform.Find("Main Panel").gameObject;
        mainPanelContent = mainPanel.transform.Find("Main Panel Content").gameObject;

        paintingInfo = mainPanel.transform.Find("Painting Info").gameObject;
        loadingText = mainPanel.transform.Find("Loading Text").gameObject;
        downloadPainting = mainPanel.transform.Find("Download Painting").GetComponent<Button>();

        sidePanel = contentContainer.transform.Find("Side Panel").gameObject;
        headerText = sidePanel.transform.Find("Header Text").gameObject;
        inputField = sidePanel.transform.Find("Input Field").gameObject;
        scrollView = sidePanel.transform.Find("Scroll View").gameObject;
        viewport = scrollView.transform.Find("Viewport").gameObject;
        content = viewport.transform.Find("Content").gameObject;

        

        scrollbarVertical = scrollView.transform.Find("Scrollbar Vertical").gameObject;

        suggestionDropDown = sidePanel.transform.Find("Suggestions Dropdown").gameObject;
        typeDropDown = sidePanel.transform.Find("Type Dropdown").gameObject;
        classificationDropdown = sidePanel.transform.Find("Classification Dropdown").gameObject;

        inputFieldComponent = inputField.GetComponent<TMP_InputField>();

        thumbnailsDownloadButton = scrollView.transform.Find("Thumbnails Button").GetComponent<Button>();
        thumbnailsDownloadButton.gameObject.SetActive(false);

        InfoPanel = mainPanel.transform.Find("Info Panel").gameObject;

        backButton = InfoPanel.transform.Find("Back Button").GetComponent<Button>();

        AppInformationButton = sidePanel.transform.Find("App Information Button").GetComponent<Button>();

        exitButton = sidePanel.transform.Find("Exit").GetComponent<Button>();

        rawImageMainPaintingPanel = mainPanelContent.GetComponent<RawImage>();



        webconnect = new Webconnect();
        paintingsDB = transform.GetComponent<PaintingsDB>();

        //RawImage translate.Find("MainPanelContent").gameObject.GetComponent<RawImage>();
        //Painting currentPaintingtransform = translate.Find("").gameObject;

        areGONull();

        allUniqueColumnAttribution = paintingsDB.getUniqueValuesByColumn("attribution").
                 Cast<string>().ToList();
        allUniqueColumnTitle = paintingsDB.getUniqueValuesByColumn("title").
                 Cast<string>().ToList();
        allUniqueColumnYearMadeIn = paintingsDB.getUniqueValuesByColumn("endyear").
                 Cast<string>().ToList();


        inputFieldComponent.onValueChanged.AddListener(delegate{
           // Debug.Log("OnInputValueModifiedOrChanged");
            OnInputValueModifiedOrChanged();
            ////UpdateSuggestionDropdownList();
            // Debug.Log("inputFieldComponent changed");
            //Debug.Log("inputFieldComponent.textComponent.text: " + inputFieldComponent.textComponent.text);
            //Debug.Log("inputFieldComponent.text: " + inputFieldComponent.text);
        });

        

        typeDropDown.GetComponent<TMP_Dropdown>().onValueChanged.AddListener(delegate
        {
            //ClearSearchTypeDropdownValues();
            Debug.Log("typeDropDown changed");
            GetArrayListWithThumbnails();
            ////UpdateSuggestionDropdownList();

        });
        
        suggestionDropDown.GetComponent<TMP_Dropdown>().onValueChanged.AddListener(delegate
        {
         //   setInputTextToSuggestion();
        });

   
        AppInformationButton.onClick.AddListener(delegate {

                InfoPanel.gameObject.SetActive(!InfoPanel.activeSelf);
            });

        downloadPainting.onClick.AddListener(delegate { DownloadPainting(currentPainting); });

        thumbnailsDownloadButton.onClick.AddListener(delegate
        {
            if (inputFieldComponent.text.Length >= minCharSearchCount)
            {
                OnSearchThumbnailsClicked();
            }
        });


        backButton.onClick.AddListener(delegate
        {
            InfoPanel.gameObject.SetActive(!InfoPanel.activeSelf);
            Debug.Log("Back button pressed");
        });

        exitButton.onClick.AddListener(delegate
        {
            Debug.Log("Exit pressed");
            Application.Quit();
        });

        classificationDropdown.GetComponent<TMP_Dropdown>().onValueChanged.AddListener(delegate
        {
            reloadContent();
        });

        paintingInfo.SetActive(false);
        loadingText.SetActive(false);
        downloadPainting.gameObject.SetActive(false);

        ////UpdateSuggestionDropdownList();

        //classificationDropdown.GetComponent<TMP_Dropdown>().OnPointerClick

        //classificationDropdown.GetComponent<TMP_Dropdown>().interactable = false;

    }

    public void OnPointerClick(PointerEventData pointerEventData)
    {
    }

        public void _OnPointerClick(PointerEventData pointerEventData)
    {

        pointerEventData.pointerClick = classificationDropdown;

        if (pointerEventData.pointerClick = classificationDropdown)
        {
            Debug.Log(name + " Game Object Right Clicked!");
        }

        //Use this to tell when the user right-clicks on the Button
            if (pointerEventData.button == PointerEventData.InputButton.Right)
        {
            //Output to console the clicked GameObject's name and the following message. You can replace this with your own actions for when clicking the GameObject.
            Debug.Log(name + " Game Object Right Clicked!");
        }

        //Use this to tell when the user left-clicks on the Button
        if (pointerEventData.button == PointerEventData.InputButton.Left)
        {
            Debug.Log(name + " Game Object Left Clicked!");
        }
    }

    public void OnValueChanged(Int32 i)
    {
        int value = 1; //this.inputField.value;
        switch (value)
        {
            case 0:
                break;
            case 1:
                break;
        }
        }

    private void _setInputTextToSuggestion()
    {
        string textSelected = GetDropdownStringInputSelected(suggestionDropDown, false);

        if (textSelected != "Suggestions" && textSelected.Length >= minCharSearchCount)
        {
           // Debug.Log("Input.text = textSelected;");
            inputFieldComponent.text = textSelected;
        }
    }

    private void OnInputValueModifiedOrChanged()
    {
        ////ResetSuggestionDropBox();

        ////UpdateSuggestionDropdownList();
        // Debug.Log("inputFieldComponent.textComponent.text.Length: " + inputFieldComponent.textComponent.text.Length);
        // Debug.Log("inputFieldComponent.text.Length: " + inputFieldComponent.text.Length);
        GetArrayListWithThumbnails();
  
    }

    // Update is called once per frame
    private void Update()
    {
        if (Input.GetKey("escape"))
        {
            Application.Quit();
        }
    }

    /// <summary>
    /// Returns a string representation of GameObject with Dropdown.
    /// Set typeList to true if the dropdown is the Search Type dropdown.
    /// </summary>
    /// <param name="gameObject"></param>
    /// <param name="typeList"></param>
    /// <returns></returns>
    private string GetDropdownStringInputSelected(GameObject gameObject, bool typeList)
    {
        //get the selected index
        int dropDownMenuIndex = gameObject.GetComponent<TMP_Dropdown>().value;

        //get all options available within this dropdown menu
        List<TMP_Dropdown.OptionData> dropdownSearchTypeOptionList = gameObject.GetComponent<TMP_Dropdown>().options;

        string selectedText = dropdownSearchTypeOptionList[dropDownMenuIndex].text;

        if (typeList)
        {
            selectedText = NGACalculationHelper.TranslateDropdownSearchColumnName(selectedText);
        }

        //Debug.Log("Inputmode is " + inputMode);

        return selectedText;
    }

    IEnumerator ScrollToTop(ScrollRect scrollRect)
    {
        yield return new WaitForEndOfFrame();
        scrollRect.gameObject.SetActive(true);
        scrollRect.verticalNormalizedPosition = 1f;
    }

    private long tickCount;

    public bool isItSafeToSearch()
    {
        //Environment.TickCount & Int32.MaxValue;

        if (tickCount < System.Environment.TickCount)
        {
            tickCount = System.Environment.TickCount + 500;

            // Debug.Log(tickCount - System.Environment.TickCount);

            return true;
        }

        //text.text = "Loading Image";
        Debug.LogWarning("UnityWebRequestTexture.GetTexture Spam Prevented.");
        return false;
    }

    private List<GameObject> GetArrayListWithThumbnailsStep2()
    {
        downloadPainting.gameObject.SetActive(false);

        string inputMode = GetDropdownStringInputSelected(typeDropDown, true);
        bool like = true; //inputMode == "title";

        List<GameObject> list = SearchAndPopulateThumbNailsByColumnNamePainting(
         inputMode, inputFieldComponent.text, true, like); // .text?

        list = sortContent(list);
        reloadContent();

        StartCoroutine(ScrollToTop(scrollView.GetComponent<ScrollRect>()));

        return list;
    }

    IEnumerator GetArrayListWithThumbnailsWaiter(List<GameObject> list, int seconds)
    {
        setLoadingText("Processing ...");
        getArrayListWithThumbnailsIsRunning = true;

         yield return new WaitForSeconds(seconds);

        list = GetArrayListWithThumbnailsStep2();
        if(list != null && list.Count > 0)
        {
            thumbnailsDownloadButton.gameObject.SetActive(true);
        }
        getArrayListWithThumbnailsIsRunning = false;
        // setLoadingText("Process complete");
    }

    IEnumerator co;
    bool getArrayListWithThumbnailsIsRunning = false;

    private void StopThumbnailDownloadCoroutineIfRunning()
    {
        if (getArrayListWithThumbnailsIsRunning)
        {
            if (co != null && getArrayListWithThumbnailsIsRunning)
            {
                Debug.Log("StopCoroutine(co)");
                StopCoroutine(co);
            }
        }
    }

    // If 1 sec passed since last call, then it's ok to call.
    // If 1 sec has not yet passed, wait 1 sec.
    private void GetArrayListWithThumbnails()
    {

        if (inputFieldComponent.text.Length >= minCharSearchCount)
        {
            Debug.Log("Searching for " + inputFieldComponent.text);

            // Code in this IF statement can only be called once every 1 seconds.
            //if (tickCount > System.Environment.TickCount) // Has one sec passed?
            // If counter is bigger than the current time then hence not 1 sec has passed
            // since last call
            //{

            List<GameObject> list = new List<GameObject>();

            StopThumbnailDownloadCoroutineIfRunning();
            
                co = GetArrayListWithThumbnailsWaiter(list, 1);
                Debug.Log("StartCoroutine(co)");
                StartCoroutine(co); // Wait 1 sec
            

            //Debug.Log("--------------------- Waiting ---------------------");

            //  Debug.Log("--------------------- Done Waiting ---------------------");
            //tickCount = System.Environment.TickCount + 1000; // Reset counter
            //}
            //else
            //{
            //   GetArrayListWithThumbnailsWaiter(new ArrayList(), 1);
            //}

            //StartCoroutine(ScrollToTop(scrollbarVertical.GetComponent<ScrollRect>()));
        }
        else if (inputFieldComponent.text.Length < minCharSearchCount)
        {
            clearContent();
        }

        
    }

    void OnSearchThumbnailsClicked()
    {
        setLoadingText("Searching for " + inputFieldComponent.text); // component
        StartCoroutine(fetchThumbNailRawTextures(GetArrayListWithThumbnailsStep2()));
    }

    private void DownloadPainting(Painting painting/*object sender, RoutedEventArgs e*/)
    {
        Debug.Log("Downloading Painting");
        if (painting != null)
        {
            using (WebClient wc = new WebClient())
            {
                string fileName = NGACalculationHelper.ConcatStringTo50(painting.Attribution) + " - " +
                    NGACalculationHelper.ConcatStringTo50(painting.Title);

                Uri uri = new Uri(painting.FullURL);
                string filename = System.IO.Path.GetFileName(uri.LocalPath);
                string extension = Path.GetExtension(filename);
                //"/NGArt Viewer Downloads/"

                // Path.DirectorySeparatorChar + "Downloaded Artworks" +
                string uriString = Directory.GetCurrentDirectory() + Path.DirectorySeparatorChar + "Downloaded Artworks" + Path.DirectorySeparatorChar +  fileName + extension;
                Debug.Log(painting.FullURL);

                wc.DownloadFileAsync(
                    // Param1 = Link of file
                    new System.Uri(painting.FullURL),
                    // Param2 = Path to save // "/NGArt Viewer Downloads/" 
                    uriString
                );
                setLoadingText("Download location: " + uriString);
            }
        }
        else
        {
            Debug.LogWarning("Current Painting is null!");
        }
    }

    private List<GameObject> sortContent(List<GameObject> list)
    {
        List<GameObject> listSorted = new List<GameObject>();

        if (list != null)
        {
            IEnumerable<GameObject> query = list.OrderBy(item => item.GetComponent<Painting>().Attribution); 

            foreach (GameObject gameObject in query)
            {
                gameObject.transform.SetParent(content.gameObject.transform);
                listSorted.Add(gameObject);
            }
        }

        return listSorted;
    }

    private void reloadContent()
    {

        string textSelected = GetDropdownStringInputSelected(classificationDropdown, false);

        if (textSelected != "Any Type of Art")
        {
            foreach (Transform child in content.transform)
            {
                if (child.gameObject.GetComponent<Painting>().Classification == textSelected)
                {
                    if (!child.gameObject.activeSelf)
                    {
                        child.gameObject.SetActive(true);
                    }
                }
                else
                {
                    if (child.gameObject.activeSelf)
                    {
                        child.gameObject.SetActive(false);
                    }
                }
            }
        }
        else
        {
            foreach (Transform child in content.transform)
            {
                if (!child.gameObject.activeSelf)
                {
                    child.gameObject.SetActive(true);
                }
            }
        }
    }

    private void clearContent()
    {
        foreach (Transform child in content.transform) { 
            GameObject.Destroy(child.gameObject); 
        }
    }

    public string GenerateArtSearchResults(int panelPaintingObjectListCount)
    {
        return panelPaintingObjectListCount + (panelPaintingObjectListCount > 1 ? " artworks found" : " artwork found");
    }

    public List<GameObject> SearchAndPopulateThumbNailsByColumnNamePainting(string columnName, string searchValue, bool like, bool any)
    {
        clearContent();

        // Get PanelPainting objects with Painting (scripts) added, populated with info from DB.
        List<GameObject> panelPaintingObjectList = paintingsDB.getPanelPaintingListFromColumname(panelPaintingPrefab, columnName, searchValue, like, any);

        if (panelPaintingObjectList != null && panelPaintingObjectList.Count > 0)
        {
            setLoadingText(GenerateArtSearchResults(panelPaintingObjectList.Count));
            Debug.Log("Paintings found in DB: " + panelPaintingObjectList.Count);

            
            //suggestionDropDown.GetComponent<TMP_Dropdown>().captionText.text = (panelPaintingObjectList.Count + " artworks found");

            //foreach (Painting painting in panelPaintingObjectList)
            foreach (GameObject obj in panelPaintingObjectList)
            {
                
                // obj.transform.SetParent(content.gameObject.transform); Later, sorting

                Painting painting = obj.GetComponent<Painting>();
                //Debug.Log(painting.ToString());
                //setEmptyTextureInRightAspectRatioForMainPanel(paintingGO.transform.Find("Panel").gameObject.transform.Find("Image").gameObject.GetComponent<RawImage>());
                obj.transform.Find("Panel").gameObject.transform.transform.Find("Image").gameObject.transform.Find("Text").GetComponent<TextMeshProUGUI>().text = painting.Attribution + "\n \n" +
                    painting.Title;
                obj.transform.Find("Panel").GetComponent<Button>().
                    onClick.AddListener(delegate { GetClickedPaintingForDownload(obj); });
                if(obj.transform.GetComponent<Painting>() != null)
                {
                    if(painting.Texture2DThumb != null)
                    {
                        RawImage rawImage = obj.transform.Find("Panel").gameObject.transform.Find("Image").gameObject.GetComponent<RawImage>();
                        rawImage.texture = painting.Texture2DThumb;
                        CanvasExtensions.SizeToParent(rawImage, 0);
                    }
                }

                ///////////loadingText.text = painting.Attribution + "\n " +
                /////   painting.Title + ". (" + painting.Endyear + "), " + painting.Classification + ", " + painting.Medium;
            }


            return panelPaintingObjectList;
        }
        else
        {
            setLoadingText(GenerateArtSearchResults(0));
            Debug.Log("No results found for " + searchValue);
            setLoadingText("No results found for " + "'" + searchValue + "'");

        }
        return null;
    }

    public void setCurrentPainting(Painting painting)
    {
        currentPainting = painting;
        downloadPainting.gameObject.SetActive(true);
    }

    public void SearchByColumnNamePaintingButtonPressed(GameObject gameO)
    {
        setEmptyTextureInRightAspectRatioForMainPanel(rawImageMainPaintingPanel);

        setLoadingText("Loading image..");

        Painting painting = gameO.GetComponent<Painting>();


            StartCoroutine(webconnect.MainPaintingPanelRequestEnumerator(painting, rawImageMainPaintingPanel));

        
        setCurrentPainting(painting);

        setPaintingPanelText(painting.Attribution + "\n " +
         painting.Title + ". (" + painting.Endyear + "), " + painting.Classification + ", " + painting.Medium);

    }

    /*
     *      Make sure only one instance is running of Coroutine is running below - half check
            Only active objects should be used
            Set bool when get set RawImage.
     * */
    IEnumerator fetchThumbNailRawTextures(List<GameObject> panelPaintingObjectList)
    {

        if (panelPaintingObjectList != null && panelPaintingObjectList.Count > 0)
        {
            // Debug.Log("Found " + panelPaintingObjectList.Count + " in panelPaintingObjectList");

            bool hasFixedRectPos = false;
            foreach (GameObject obj in panelPaintingObjectList)
            {
                if (obj != null && obj.activeSelf)
                {
                 
                    // Debug.Log("Found " + painting.Objectid);

                    setLoadingText("Downloading image thumbnails...");
                    StartCoroutine(webconnect.PaintingRequestEnumeratorFreeStyleThumbnail(obj));

                    if (!hasFixedRectPos)
                    {
                        hasFixedRectPos = true;
                    }

                    thumbnailsDownloadButton.gameObject.SetActive(false);

                    yield return new WaitForSeconds(0.5f);
                }
            }
            setLoadingText("Search Complete");
        }
    }

    // Get current type-dropdown value
    // Get corresponding List depending on above value
    // Fill the suggestion List with filtered values from above list 
    private void _UpdateSuggestionDropdownList()
    {
        string selectedType = GetDropdownStringInputSelected(typeDropDown, true); // was false
        string selectedClassification = GetDropdownStringInputSelected(classificationDropdown, false);
        List<string> selectedList = TranslateTypeToCorrespondingList(selectedType);

       // Debug.Log("Number of unique values in " + selectedType + ": " + selectedList.Count);


        if (selectedType != "Title" && inputFieldComponent.text.Length >= minCharSearchCount ||
            (inputFieldComponent.text.Length >= minCharSearchCount + 2))
        {
            //ResetSuggestionDropBox();
            foreach (string t in selectedList)
            {
                if (t.Contains(inputFieldComponent.text))
                {
                    suggestionDropDown.GetComponent<TMP_Dropdown>().options.Add(new TMP_Dropdown.OptionData() { text = t });
                } // t.StartsWith(inputFieldComponent.text)
            }

        }
    }

    public void setEmptyTextureInRightAspectRatioForMainPanel(RawImage rawI)
    {
        mainPanelContent.GetComponent<RectTransform>().sizeDelta = mainPanel.GetComponent<RectTransform>().sizeDelta;
        downloadPainting.gameObject.SetActive(false);
        rawI.texture = new Texture2D((int)mainPanel.GetComponent<RectTransform>().rect.width, (int)mainPanel.GetComponent<RectTransform>().rect.height);
    }

    void GetClickedPaintingForDownload(GameObject obj)
    {
        // Debug.Log(obj.GetComponent<Painting>().Objectid + " button pressed");
        // Set thumbnail painting here

        StartCoroutine(webconnect.PaintingRequestEnumeratorFreeStyleThumbnail(obj));
        // , obj.transform.Find("Panel").gameObject.transform.Find("Image").
       // gameObject.GetComponent<RawImage>()

        SearchByColumnNamePaintingButtonPressed(obj);
    }

    private void _ClearSearchTypeDropdownValues()
    {
        suggestionDropDown.GetComponent<TMP_Dropdown>().options.Clear();
        suggestionDropDown.GetComponent<TMP_Dropdown>().itemText.text = "Suggestions";
        suggestionDropDown.GetComponent<TMP_Dropdown>().captionText.text = "Suggestions";
    }

    private void _ResetSuggestionDropBox()
    {
        suggestionDropDown.GetComponent<TMP_Dropdown>().options.Clear();
        suggestionDropDown.GetComponent<TMP_Dropdown>().options.Add(new TMP_Dropdown.OptionData() { text = "Suggestions" });
        suggestionDropDown.GetComponent<TMP_Dropdown>().value = 0;
        //suggestionDropDown.GetComponent<TMP_Dropdown>().captionText.text = "Any";
    }

    private void setLoadingText(string text)
    {
        loadingText.SetActive(true);
        loadingText.GetComponent<TextMeshProUGUI>().text = text;
    }

    private void setPaintingPanelText(string text)
    {
        loadingText.SetActive(false);
        paintingInfo.SetActive(true);
        paintingInfo.GetComponent<TextMeshProUGUI>().text = text;
    }

    public void setEmptyTextureInRightAspectRatioForThumbnail(GameObject panelImage)
    {
        panelImage.GetComponent<RectTransform>().sizeDelta = panelImage.transform.parent.GetComponent<RectTransform>().sizeDelta;
    }

    private List<string> TranslateTypeToCorrespondingList(string type)
    {
        if (type == "attribution")
        {
            return allUniqueColumnAttribution;
        }
        else if (type == "title")
        {
            return allUniqueColumnTitle;
        }
        else if (type == "endyear")
        {
            return allUniqueColumnYearMadeIn;
        }

        Debug.LogWarning("TranslateTypeToCorrespondingList() Failed!");
        return allUniqueColumnTitle;
    }

    private void areGONull()
    {
        NGACalculationHelper.IsGameObjectNull(contentContainer);
        NGACalculationHelper.IsGameObjectNull(mainPanel);
        NGACalculationHelper.IsGameObjectNull(mainPanelContent);
        NGACalculationHelper.IsGameObjectNull(paintingInfo);
        NGACalculationHelper.IsGameObjectNull(loadingText);
        NGACalculationHelper.IsGameObjectNull(sidePanel);
        NGACalculationHelper.IsGameObjectNull(headerText);
        NGACalculationHelper.IsGameObjectNull(inputField);
        NGACalculationHelper.IsGameObjectNull(scrollView);
        NGACalculationHelper.IsGameObjectNull(viewport);
        NGACalculationHelper.IsGameObjectNull(content);
        NGACalculationHelper.IsGameObjectNull(scrollbarVertical);
        //NGACalculationHelper.IsGameObjectNull(suggestionDropDown);
        NGACalculationHelper.IsGameObjectNull(typeDropDown);
    }

}