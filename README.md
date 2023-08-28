# Ruxx
[Download](https://github.com/trickerer01/Ruxx/releases/) [latest release](https://github.com/trickerer01/Ruxx/releases/latest/) (Windows, Linux)  
[![Downloads](https://img.shields.io/github/downloads/trickerer01/Ruxx/total?color=brightgreen&style=flat)](https://github.com/trickerer01/Ruxx/releases/)

### What the hell?
Ruxx is a content downloader with a lot of filters for maximum search precision (and ugly GUI). Supported sites are on your right

### How to use
- \[Optional] Choose a **Module** (website) to use. Notice that an icon in the bottom left corner will change accordingly
- Fill the **Tags** field with tags you want to search for. For base and quick advanced info on tags check **Help -> Tags** section. [More info](#tags-syntax)
- \[Optional] Additonally, check the **filters** to fine-tune your search. You can choose whether you want do download **videos**, **images** or **both**, add **post date** limits, number of **download threads**
- \[Optional] Choose the destination **Path**. Default path is current folder
- Press **Download**

![Ruxx](https://github.com/trickerer01/Ruxx/assets/76029665/83580f95-a4c3-4827-b5f4-5a6838bf8886)

Note that Ruxx does not restrict your searches to a couple pages or something. You may even search for something like *id:>=0* (everything), this won't work though as websites actually put a limit on maximum search results returned. For something stupid like this you'll have to split your searches using id filter. Plus you may still get banned for abusing the resource. **Ruxx is not a scraping tool**

#### Filters
- *Videos* ‒ some websites serve videos in multiple formats, here you can select a prefered one. **Redundant since 01.05.2021 (RX internal changes)**. You may also exclude videos altogether
- *Images* ‒ some websites serve images in multiple resolutions / quilities (full, preview), which you can choose from. Just like with the videos, you can also filter all the images out
- *Parent posts / child posts* ‒ this switch allows to, in addition to initial search result, also download parent posts, all children and all found parents' children even if they don't match the tags you're searching for. RX only
- *Threading* ‒ the number of threads to use for downloading. This also somewhat increases the number of scan threads. More threads means speed, less threads means less network hiccups. Max threads is not a problem in most cases, but you must always remember that nobody likes reckless hammering of their services/APIs
- *Date min / max* ‒ applied to initial search results, format: `dd-mm-yyyy`, ignored if set to default (min: `01-01-1970`, max: `<today>`). Enter some gibberish to reset do default

#### Misc & Tools
- **File -> Save settings...** \<Ctrl+S> ‒ allows you to save current run parameters to a config file for later or as a template
- **File -> Load settings...** \<Ctrl+O> ‒ load run parameters from previously saved config file. You can also put a `.cfg` file folder with executable and Ruxx will automatically pick it and configure itself. You have to use one of the following names: ['ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg']
- **File -> Reset all settings** ‒ resets all settings to initial ones. If autoconfigured this will reset to those parameters
- **File -> Open download folder** \<Ctrl+L> ‒ open currently selected destination folder (**Path**), Windows only
- **View -> Log** ‒ open a log window, if you want some readable output
- **Edit -> Prefix file names with \<prefix>** ‒ all downloaded files will be named accordingly and not as just numbers. This option is enabled by default
- **Edit -> Save tags** ‒ an additional (text) file will be created containing tags for every file. Row format is `<file>: <score> <tags>`
- **Edit -> Save source links** ‒ an additional (text) file will be created containing source (if present) for every file. Row format is `<file>: <source>`
- **Edit -> Extend file names with extra info** ‒ all file names will include short representation of their major tags if any. This may extend resulting full path up to 240 symbols total
- **Edit -> Warn if donwload folder is not empty** ‒ in GUI mode you will be warned if destination folder is not empty and there is a potential risk of mixing up different search results
- **Connection -> Headers / Cookies** \<F3> ‒ solely to work with cloudflare protected websites (RN). You'll have to provide your `cf_clearance` cookie, and the `user-agent` header has to match the one used in your web browser for target wesite ‒ to find it while browsing said website open `Web Developer tools -> Network`, reload the page and check `request headers`
- **Connection -> Set proxy** \<F4> ‒ you can use proxy if you want or if target website is blocked in your country. SOCKS5 proxies are supported too
- **Connection -> Set timeout** \<F5> ‒ override connection timeout if need be
- **Connection -> Download without proxy** ‒ you can use this option for RX if only the main domain is blocked in your country
- **Connection -> Ignore proxy** ‒ this is just a switch to disable proxy temporarily without wiping it
- **Actions -> Download** \<Ctrl+Shift+D> ‒ same as download button
- **Actions -> Check tags** \<Ctrl+Shift+C> ‒ same as check tags button
- **Tools -> Load from ID list** ‒ Allows you to load **ID** tag list from a text file. The resulting tags will look like `(id:x~id:y~id:z)` which is an ***OR*** group expression, effectively allowing you to search for those ids. ~~Broken since about 10.07.2021. Refer to "Broken things" RX forum subsection for details.~~ Re-enabled since version `1.1.284` for both RX and RN using a workaround, but doesn't run in parallel so be aware of that
- **Tools -> Un-tag files...** ‒ renames selected Ruxx-downloaded media files, stripping file names of all extra info
- **Tools -> Re-tag files...** ‒ renames selected Ruxx-downloaded media files, re-appending extra info. You'll need dumped tags info file(s) (see **Edit -> Save tags**)
- **Tools -> Sort files into subfolders...** ‒ a set of tools to separate downloaded files if need be:
    - **by type** ‒ sort by file type (checking file extension). You can separate files by `videos`/`images`/`flash (RN)` or by extension itself. Note that both `jpeg` and `jpg` files will be moved into **jpg** folder
    - **by size** ‒ sort by file size (you'll have to provide a threshold, in Megabytes). You can use multiple thesholds, separated by space: `0.5 10 3.0 5.00`
    - **by score** ‒ sort by post score. Make sure that selected files include score in their names or this won't work. You can use multiple thesholds, separated by space: `100 250 50 500`
- **Help -> Tags** ‒ a quick list of tag types and how to use them (for selected module)
- **Tags checking** ‒ there is a small button near the **Tags** field. When pressed, Ruxx will try to connect to the website to see if this search yields any results. As a result the **Tags** field will briefly flash green / red. Additionally, if result is positive, a window will appear with exact number of results found

### Tags syntax
Ruxx normally allows most symbols for tags search, there are some specifics though:  
1. Wildcards
- Both RX and RN support asterisk symbol `*` as wildcard in tags (any number of any symbols). You can use any number of wildcards in tags in any place: `b*m*_cit*`
  - Note that there is a bug in RX search engine which breaks frontal wildcards: `*_city` will work for RN but RX will return default result (all)
2. Meta tags
- Meta tags describe not the posted artwork but the post itself. Both RX and RN support meta tags
  - RX syntax: _name_**:**_value_ OR _name_**:=**_value_
  - RN syntax: _name_**=**_value_
- Meta `-tags` can be used for exclusion: `-rating:explicit`
- Some meta tags support wildcards. Rules are very strict so this feature is yet to be enabled in Ruxx
- Some meta tags support inequality. These metatags can be used to set a range, ex. `id:>X id:<Y`. See below for more syntax
  - Note that meta `-tags` cannot be used with inequality, like `-score:<0`. Flip the comparison instead: `score:>=0`.
- Although 'ordering' meta tags exist for both RX and RN (`sort` and `order` respectively), you can't use them. Posts are always sorted by id
- RX meta tags:
  - **id**: `id:X` (or `id:=X`), `id:>X`, `id:<Y`, `id:>=X`, `id:<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score:X` (or `score:=X`), `score:>X`, `score:<Y`, `score:>=X`, `score:<=Y`. `X`,`Y` = `<number>`
  - Rarely used ones:
    - parent: `parent:X` (or `parent:=X`). `X` = `<post ID>`
    - width: `width:X` (or `width:=X`), `width:>X`, `width:<Y`, `width:>=X`, `width:<=Y`. `X`,`Y` = `<number>`
    - height: `height:X` (or `height:=X`), `height:>X`, `height:<Y`, `height:>=X`, `height:<=Y`. `X`,`Y` = `<number>`
    - user: `user:X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating name>`, ex. `safe`, `questionable`, `explicit`.
    - md5: `md5:X`, `X` = `<MD5 hash>`
    - source:
    - updated:
    - ~~sort~~:
- RN meta tags:
  - **id**: `id=X`, `id>X`, `id<Y`, `id>=X`, `id<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score=X`, `score>X`, `score<Y`, `score>=X`, `score<=Y`. `X`,`Y` = `<number>`
  - Rarely used ones:
    - width: `width=X`, `width>X`, `width<Y`, `width>=X`, `width<=Y`. `X`,`Y` = `<number>`
    - height: `height=X`, `height>X`, `height<Y`, `height>=X`, `height<=Y`. `X`,`Y` = `<number>`
    - user: `user=X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating letter>`, ex. `q`, `s`, etc.
    - ~~order~~:
3. `OR` groups
- Ruxx syntax for `OR` is simplified compared to what you would normally use for RX: `(tag1~tag2~...~tagN)` instead of `( tag1 ~ tag2 ~ ... ~ tagN )`
- Ruxx allows using `OR` groups for RN too
- Although using meta tags in `OR` groups is broken currently `(id:=X~score:=Y)`, Ruxx will circumvent this problem and process them properly
4. Negative groups
- Syntax: `-(tag1,tag2,...,tagN)`. Ruxx allows to filter out tag combinations (posts where all tags in group are present), which you can't normally do using website search engine. In addition to normal tag symbols, in negative group tags you can use wildcard symbols `?` and `*` for 'any symbol' and 'any number of any symbols' repectively. You can also use pipe symbol `|` for direct regex `or` group composition. Example: `-(tag?1,ta*g2|tag3)` will be effectively converted to regexes `"^tag.1$"` and `"^ta.*g2|tag3$"` to check for, posts with tags matching both will get filtered out
    - Important note: unlike normal `-tags`, negative group will not check tag aliases
5. Tags number limits
- Any valid search query requires at least one positive tag to search for. Search query cannot be formed using `-tags` only
- Very long search queries will cause website to return empty result. Generally this happens when trying to add too many `-tags` to narrow down the search. If resulting query is too long Ruxx will automatically create a specific [negative group](#tags-syntax) from excessive `-tags` and use them as an additional filter. The message will be given as follows: `<X> 'excluded tags combination' custom filter(s) parsed`

#### User credentials
Ruxx doesn't provide a method of authentication natively on either of supported sites. To use your identity during search you need to follow 3 simple steps:
- Log in normally using web browser
- Open `Web Developer tools -> Network` and reload the page, look for `request headers`
- Open `Headers / Cookies` window `<F3>` and fill the tables accordingly:
  - Headers: `user-agent` (remove existing value first)
  - Cookies:
    - RX: `cf_clearance`, `user_id`, `pass_hash`
    - RN: `cf_clearance`, `shm_user`, `shm_session`

#### Using from console
It is possible to use Ruxx as a cmdline tool. In main window you will find a `Cmd` section ‒ it generates your cmdline arguments every time you make a change ‒ use those arguments as an example. In console window you may need to escape some of them (path, 'or' groups, tags containing dot(s), etc.). Most arguments are optional though ‒ the only ones required are `tags` (default module is RX)  
Invoke `Ruxx --help` for full help

#### Logging
Ruxx will log most of its actions, which you can see in **Log** window  
If any problem occurs it will yield some info unless it's an unexpected fatal error. Ruxx is able to resolve most non-fatal networking errors and IO mishaps, including dropped searches (search overload), non-matching e-tags, file size mismatch, malformed packets, etc.
- **W1**: a minor problem, more of the info
- **W2**: a problem which is going to be fixed, but there is no guarantee it won't occur again
- **W3**: a rather serious problem, Ruxx will attempt to fix it, but it may be not enough, may lead to an error down the road
- **ERROR**: if you see this the download process may fail, Ruxx can only retry the failed action, in most cases that's enough

### Technical info
Ruxx is written is Python (3.7). Lines of code: 8000+. Executables built using PyInstaller (5.8 for Windows, 3.6 for Linux)

### Support
Did I help you? Maybe you wish to return the favor  
[Donate](https://paypal.me/trickerer)
