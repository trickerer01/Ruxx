# Ruxx
[Download](https://github.com/trickerer01/Ruxx/releases/) [latest release](https://github.com/trickerer01/Ruxx/releases/latest/) (Windows, Linux)  
[![Downloads](https://img.shields.io/github/downloads/trickerer01/Ruxx/total?color=brightgreen&style=flat)](https://github.com/trickerer01/Ruxx/releases/)

### What the hell?
Ruxx is a content downloader with a lot of filters for maximum search precision (and ugly GUI). Supported sites are on your right

### How to use
- \[Optional] Choose a **Module** (website) to use. Notice that an icon in the bottom left corner will change accordingly
- Fill the **Tags** field with tags you want to search for. For base and quick advanced info on tags check **Help -> Tags** section. [More info](#tags-syntax)
- \[Optional] Additonally, check the **filters** to fine-tune your search. You can choose whether you want do download **videos**, **images**, or **both**, add **id** and **post date** limits, as well as number of **download threads** and **download order**
- \[Optional] Choose the destination **Path**. Default path is current folder
- Press **Download**

![rx](https://user-images.githubusercontent.com/76029665/196680406-b76e4766-0832-4a08-953f-27b41f9636e5.JPG)

Note that Ruxx does not restrict your searches to a couple pages or something. You may even search for something like *id:>=0* (everything), this won't work though as websites actually put a limit on maximum search results returned. For something stupid like this you'll have to split your searches using id filter. Plus you may still get banned for abusing the resource. **Ruxx is not a scraping tool**

#### Filters
- *Videos* - some websites serve videos in multiple formats, here you can select a prefered one. **Redundant since 01.05.2021 (RX internal changes)**. You may also exclude videos altogether
- *Images* - some websites serve images in multiple resolutions / quilities (full, preview), which you can choose from. Just like with the videos, you can also filter all the images out
- *Threading* - the number of threads to use for downloading. This also somewhat increases the number of scan threads. More threads means speed, less threads means less network hiccups. Actually even max threads is no problem in most cases
- *Order* - the download queue is sorted by ID which directly correlates with upload time. `Oldest first` means ascending order. If you really care
- *Search limits*
  - *Date min / max* - applied to initial search results, format: `dd-mm-yyyy`, ignored if set to default (min: `01-01-1970`, max: `<today>`). Enter some gibberish to reset do default
  - *ID min / max* - these are applied directly to your searches (transformed into tags), unless tags string already contains respective id tags. You can set `max` to a negative value to make it serve as `count` (GUI only)

#### Misc & Tools
- **File -> Save settings...** \<Ctrl+S> - allows you to save current run parameters to a config file for later or as a template
- **File -> Load settings...** \<Ctrl+O> - load run parameters from previously saved config file. You can also put a `.cfg` file folder with executable and Ruxx will automatically pick it up to configure itself. You have to use one of the following names: ['ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg']
- **File -> Reset all settings** - resets all settings to initial ones. If autoconfigured this will reset to those parameters
- **File -> Open download folder** \<Ctrl+L> - open currently selected destination folder (**Path**), Windows only
- **View -> Log** - open a log window, if you want some readable output
- **Edit -> Prefix file names with \<prefix>** - all downloaded files will be named accordingly and not as just numbers. This option is enabled by default
- **Edit -> Save tags** - an additional (text) file will be created containing tags for every file. Row format is `<file>: <score> <tags>`
- **Edit -> Save source links** - an additional (text) file will be created containing source (if present) for every file. Row format is `<file>: <source>`
- **Edit -> Extend file names with extra info** - all file names will include short representation of their major tags if any. This may extend resulting full path up to 240 symbols total
- **Edit -> Warn if donwload folder is not empty** - in GUI mode you will be warned if destination folder is not empty and there is a potential risk of mixing up different search results
- **Connection -> Headers / Cookies** \<F3> - solely to work with cloudflare protected websites (RN). You'll have to provide your `cf_clearance` cookie, and the `user-agent` header has to match the one used in your web browser for target wesite - to find it while browsing said website open `Web Developer tools -> Network`, reload the page and check `request headers`
- **Connection -> Set proxy** \<F4> - you can use proxy if you want or if target website is blocked in your country. SOCKS5 proxies are supported too
- **Connection -> Download without proxy** - you can use this option for RX if only the main domain is blocked in your country
- **Connection -> Ignore proxy** - this is just a switch to disable proxy temporarily without wiping it
- **Actions -> Download** \<Ctrl+Shift+D> - same as download button
- **Actions -> Check tags** \<Ctrl+Shift+C> - same as check tags button
- **Tools -> Load from ID list** - Allows you to load **ID** tag list from a text file. The resulting tags will look like `(id:x~id:y~id:z)` which is an ***OR*** group expression, effectively allowing you to search for those ids. ~~**Broken since about 10.07.2021. Refer to "Broken things" RX forum subsection for details**~~. UPD re-enabled since version `1.1.284` for both RX and RN using a workaround, but doesn't run in parallel so be aware of that
- **Tools -> Un-tag files...** - renames selected Ruxx-downloaded media files, stripping file names of all extra info
- **Tools -> Re-tag files...** - renames selected Ruxx-downloaded media files, re-appending extra info. You'll need dumped tags info file(s) (see **Edit -> Save tags**)
- **Tools -> Sort files into subfolders...** - a set of tools to separate downloaded files if need be:
    - **by type** - sort by file type (checking file extension). You can separate files by `videos`/`images`/`flash (RN)` or by extension itself. Note that both `jpeg` and `jpg` files will be moved into **jpg** folder
    - **by size** - sort by file size (you'll have to provide a threshold, in Megabytes). You can use multiple thesholds, separated by space: `0.5 10 3.0 5.00`
    - **by score** - sort by post score. Make sure that selected files include score in their names or this won't work. You can use multiple thesholds, separated by space: `100 250 50 500`
- **Help -> Tags** - a quick list of tag types and how to use them (for selected module)
- **Tags checking** - there is a small button near the **Tags** field. When pressed, Ruxx will try to connect to the website to see if this search yields any results. As a result the **Tags** field will briefly flash green / red. Additionally, if result is positive, a window will appear with exact amount of results found

### Tags syntax
Ruxx normally allows most symbols for tags search, there are some specifics though:  
1. `OR` groups
- Ruxx syntax for `OR` is simplified compared to what you would normally use for RX: `(tag1~tag2~...~tagN)` instead of `( tag1 ~ tag2 ~ ... ~ tagN )`
- Ruxx allows using `OR` groups for RN too
- Although using sort tags in `OR` groups is broken currently `(id:=X~score:=Y)`, Ruxx will circumvent this problem and process them properly
2. Special tag types
- Negative group, syntax: `-(tag1,tag2,...,tagN)`. Ruxx allows you to filter tag combinations (content where all tags in the group are present), which you can't normally do using website search engine. In addition to normal tag symbols, in negative group tags you can use wildcard symbols `?` and `*` for 'any symbol' and 'any number of any symbols' repectively. You can also use pipe symbol `|` for direct regex `or` group composition. Example: `-(tag?1,ta*g2|tag3)` will be effectively converted to regexes `"^tag.1$"` and `"^ta.*g2|tag3$"` to check for, posts with tags matching both will get filtered out
    - Important note: unlike normal `-tags`, negative group will not check tag aliases
3. Tags number limits
- Any valid search query requires at least one positive tag to search for. Search query cannot be formed using `-tags` only
- Very long search queries will cause website to return empty result. Generally this happens when trying to add too many `-tags` to narrow down the search. If resulting query is too long Ruxx will automatically create a specific [negative group](#tags-syntax) from excessive `-tags` and use them as an additional filter. The message will be given as follows: `<X> 'excluded tags combination' custom filter(s) parsed`

#### Using from console
It's possible to use Ruxx as a cmdline tool. In the main window you can find a `Cmd` section. It generates your cmdline arguments every time you make a change - use those arguments as an example  
Invoke `Ruxx --help` for full help

#### Logging
Ruxx will log most of its own actions, which you can see in **Log** window  
If any problem occurs it will yield some info unless it's an unexpected fatal error. Ruxx is able to resolve most non-fatal networking errors and IO mishaps, including dropped searches (search overload), non-matching e-tags, file size mismatch, malformed packets, etc.
- **W1**: a minor problem, more of the info
- **W2**: a problem which is going to be fixed, but there is no guarantee it won't occur again
- **W3**: a rather serious problem, Ruxx will attempt to fix it, but it may be not enough, may lead to an error down the line
- **ERROR**: if you see this the download process may fail, Ruxx can only retry the failed action, in most cases that's enough

### Technical info
Ruxx is written is Python (3.7). Lines of code: 8000+. Executables are built using PyInstaller (4.2 for Windows, 3.6 for Linux)

### Support
Did I help you? Maybe you wish to return the favor  
[Donate](https://paypal.me/trickerer)
