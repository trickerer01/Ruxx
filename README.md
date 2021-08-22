# Ruxx
[Download](https://github.com/Trickerer01/Ruxx/releases/) [latest release](https://github.com/Trickerer01/Ruxx/releases/latest/) (Windows, Linux)

### What the hell?
Ruxx is a content downloader with a lot of filters for maximum search precision (and ugly interface). Supported sites are on your right.

### How to use
- \[Optional] Chose a **Module** (website) to use. Notice that an icon in the bottom left corner will change accordingly
- Fill the **Tags** you want to search for. For base and quick advanced info on tags check **Help -> Tags** section
- \[Optional] Additonally, check the **filters** to fine-tune your search. You can choose whether you want do download **videos / images**, add **id** and **post date** restrictions, as well as number of **download threads** and **download order**
- \[Optional] Chose the destination **Path**. Default path is current folder
- Press **Download**

![Main window](https://user-images.githubusercontent.com/76029665/127795331-928d6645-11c4-4be4-8533-20c628708b6b.JPG)

Note that Ruxx does not restrict your search to a couple pages or something. You may even search for something like *id:>=0* (the whole website), this won't work though as websites actually put a limit on maximum search results returned. For something stupid like this you'll have to split your searches using an id filter. Plus you may still get banned for abusing the resource. **Ruxx is not a scraping tool**

#### Filters
- *Videos* - some websites serve videos in multiple formats, which you can chose from. **Redundant since 01.05.2021 (RX internal changes)**. You may also exclude videos altogether
- *Images* - some websites serve images in multiple resolutions / quilities (full, preview), which you can chose from. You may also exclude images altogether
- *Destination* - create a subfolder in target directory and download there instead. Subfolder name is based on selected tags **and does not respect maximum path length**
- *Threading* - the number of threads to use for downloading. This also somewhat increases page scan threads. More threads means speed, less threads means safety for you and less network hiccups. Actually even max threads is no problem in most cases
- *Order* - the download queue is sorted by ID which directly correlates with upload time. `Oldest first` mean ascending order. Well, who cares really?
- *Search limits*
  - *Date min / max* - applied as filters, ignored if set to default (`01-01-1970` / `<today>`)
  - *ID min / max* - these are applied directly to your searches (converted into tags). You can set *max* to a negative value to make it serve as a `count`
- *Don't download* - this ugly thing stays there for debugging purposes. If checked the process goes as normal except all files in the final result are skipped without even trying to retrieve content info

#### Misc & Tools
- **View -> Log** - if you want some readable output
- **Edit -> Prefix file names with \<prefix>** - all downloaded files will be named accordingly and not just numbers. This option is enabled by default
- **Edit -> Save tags** - an additional (text) file will be created containing tags for every file. Format is `<file>: <tags>`
- **Edit -> Save source links** - an additional (text) file will be created containing source (if present) for every file. Format is `<file>: <source>`
- **Connection -> Headers / Cookies** - solely to work with cloudflare protected sites (RN). You'll have to provide your `cf_clearance` cookie, and the `user-agent` header has to match the one used in your web browser for target wesite - to find it while browsing said website open `Web Developer tools -> Network`, reload the page and check request headers
- **Connection -> Set proxy** - you can use proxy if you want or if target website is blocked in your country. SOCKS5 proxies are supported too
- **Connection -> Download without proxy** - you can use this option for RX if only the main domain is blocked in your country
- **Connection -> Ignore proxy** - this is just a switch to disable proxy without wiping it
- **Tools -> Load from ID list** - RX only. allows you to load **ID** tag list from a text file. The resulting tags will look like `(id:x~id:y~id:z)` which is an *OR* expression, allowing you effectively search for these ids. **Broken since about 10.07.2021. Refer to "Broken things" RX forum subsection for details**
- **Help -> Tags** - a quick list of tag types and how to use them (for selected module)
- **Tags checking** - there is a small button near the **Tags** field. When pressed, Ruxx will try to connect to the website to see if this search yields any results. As a result the **Tags** field will briefly flash green / red

#### Using from console
It is possible to use Ruxx as a cmdline tool. Currently only RX is supported. In the main window you can find a *Cmd* section. It generated your cmdline arguments every time you make a change - use those arguments as examples. Invoke `Ruxx -h` for help

#### Logging, Warnings and Errors
Ruxx will log most of its own actions, which you can see in **Log** window  
If any problem occurs it will yield some info unless it's an unexpected fatal error. Ruxx is able to resolve most non-fatal networking errors and IO mishaps, including dropped searches (search overload), non-matching e-tags, file size mismatch, malformed packets and so on - these will only produce warnings
- W1: a minor problem, more of the info
- W2: a problem which is going to be fixed, but there is no guarantee it won't occur again
- W3: a rather serious problem, Ruxx will attempt to fix it, but it may be not enough, may lead to an error down the line
- ERROR: if you see this the download process may fail, Ruxx may only retry the failed action, in most cases it is enough

### Technical info
Ruxx is written is Python (3.5). Executables are built using PyInstaller (4.2 for Windows, 3.6 for Linux)

### Support
Did I help you? Maybe you wish to return the favor  
[Donate](https://paypal.me/trickerer)  
The source code will go public if this project gets any support
