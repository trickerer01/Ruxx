# Ruxx
[Download](https://github.com/trickerer01/Ruxx/releases/) [latest release](https://github.com/trickerer01/Ruxx/releases/latest/) (Windows, Linux)  
[![Downloads](https://img.shields.io/github/downloads/trickerer01/Ruxx/total?color=brightgreen&style=flat)](https://github.com/trickerer01/Ruxx/releases/)

### What the hell?
Ruxx is a content downloader with a lot of filters for maximum search precision (and ugly GUI). Supported websites are in description, everywhere else ‒ abbreviations only

### How to use
- \[Optional] Choose **Module** (website) to use. The icon in the bottom left corner will change accordingly
- Fill the **Tags** field with tags you want to search for. For base and quick advanced info on tags check **Help -> Tags** section. [More info](#tags-syntax)
- \[Optional] Configure **filters** to fine-tune your search. You can choose whether you want do download **videos**, **images** or **both**, add **post date** limits, number of **download threads**
- \[Optional] Choose the destination **Path**. Default path is current folder
- Press **Download**

![Ruxx](https://github.com/trickerer01/Ruxx/assets/76029665/023213f4-0761-41df-a48c-43ec80041356)


Note that Ruxx does not restrict your searches to a couple pages or something. You may even search for something like *id:>=0* (everything), this won't work though as websites actually put a limit on maximum search results returned. For something stupid like this you'll have to split your searches using id filter. Plus you may still get banned for abusing the resource. **Ruxx is not a scraping tool**

#### Filters
- *Videos* ‒ some websites serve videos in multiple formats, here you can select a prefered one. **Redundant since 01.05.2021 (RX internal changes)**. You may also exclude videos altogether
- *Images* ‒ some websites serve images in multiple resolutions / quilities (full, preview), which you can choose from. Just like with the videos, you can also filter all the images out
- *Parent posts / child posts* ‒ this switch allows to, in addition to initial search result, also download parent posts, all children and all found parents' children even if they don't match the tags you're searching for. RX only
- *Threading* ‒ the number of download threads to use. This also somewhat increases the number of scan threads. More threads means speed, less threads means less network hiccups. Max threads is not a problem in most cases, but you must always remember that nobody likes reckless hammering of their services/APIs
- *Date min / max* ‒ applied to initial search results, format: `dd-mm-yyyy`, ignored if set to default (min: `01-01-1970`, max: `<today>`). Enter some gibberish to reset do default. RX and RN only

#### Misc & Tools
- **File -> Save settings...** \<Ctrl+S> ‒ allows you to save current run parameters to a config file for later or as a template. `Note that only recognized parameters will be loaded - missing parameters will just stay unchanged without any errors given, so if you want to not save some parameters (ex. window position) just remove associated rows from the file`
- **File -> Load settings...** \<Ctrl+O> ‒ load run parameters from previously saved config file. You can also put a `.cfg` file folder with executable and Ruxx will automatically pick it and configure itself. You have to use one of the following names: ['ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg']
- **File -> Reset all settings** ‒ resets all settings to initial ones. If autoconfigured this will reset to those parameters. Window position is unaffected by this action
- **File -> Open download folder** \<Ctrl+L> ‒ open currently selected destination folder (**Path**), Windows only
- **View -> Log** ‒ open a log window, if you want some readable output
- **Edit -> Prefix file names with \<prefix>** ‒ all downloaded files will be named accordingly and not as just numbers. This option is enabled by default
- **Edit -> Save tags** ‒ an additional (text) file will be created containing tags for every post
- **Edit -> Save source links** ‒ an additional (text) file will be created containing source (if present) for every post
- **Edit -> Save comments** ‒ an additional (text) file will be created containing comments (if present) for every post
- **Edit -> Save info mode...** ‒ tags/sources/comments info file save mode
  - **per run** ‒ create a single file per checked info category for every (non-empty) downloader run, this is the default mode
  - **per file** ‒ create info files per each downloaded file (not recommended)
  - **merge info lists** ‒ gather and parse existing info files, merge and save all infos together, one text file per info category will be stored. **Parsed old info files will be deleted**
- **Edit -> Extend file names with extra info** ‒ all file names will include short representation of their major tags if any. This may extend resulting full path up to 240 symbols total
- **Edit -> Warn if download folder is not empty** ‒ in GUI mode you will be warned if destination folder is not empty and there is a potential risk of mixing up different search results
- **Edit -> Verbose log** ‒ Enable logging of technical messages not related to actual download process. Verbose log is one of proper issue report requirements
- **Connection -> Headers / Cookies** \<F3> ‒ For some websites (RN) and in some other cases you'll have to provide your `cf_clearance` cookie, and the `User-Agent` header has to match the one used in your web browser for target website ‒ to find it while browsing said website open `Web Developer tools -> Network` (or similar), reload the page and check `request headers`
- **Connection -> Set proxy** \<F4> ‒ you can use proxy if you want or if target website is blocked in your country. SOCKS5 proxies are supported too
- **Connection -> Set timeout** \<F5> ‒ override connection timeout if need be
- **Connection -> Set retries count** \<F6> ‒ override connection retries count, may be useful when using proxy
- **Connection -> Download without proxy** ‒ you can use this option for RX if only the main domain is blocked in your country
- **Connection -> Ignore proxy** ‒ this is just a switch to disable proxy temporarily without wiping it
- **Connection -> Cache processed HTML** ‒ by default HTML is cached as raw bytes, enabling this makes Ruxx cache HTML after it was processed into manageable form - a little bit faster but consumes much more memory. Mainly affects RS module
- **Actions -> Download** \<Ctrl+Shift+D> ‒ same as download button
- **Actions -> Check tags** \<Ctrl+Shift+C> ‒ same as check tags button
- **Tools -> Load from ID list** ‒ Allows you to load **ID** tag list from a text file. The resulting tags will look like `(id:x~id:y~id:z)` which is an ***OR*** group expression, effectively allowing you to search for those ids. ~~Broken since about 10.07.2021. Refer to "Broken things" RX forum subsection for details.~~ Re-enabled since version `1.1.284` for all (RX, RS and RN) modules using a workaround, but doesn't run in parallel so be aware of that
- **Tools -> Un-tag files...** ‒ renames selected Ruxx-downloaded media files, stripping file names of all extra info
- **Tools -> Re-tag files...** ‒ renames selected Ruxx-downloaded media files, re-appending extra info. You'll need dumped tags info file(s) (see **Edit -> Save tags**)
- **Tools -> Sort files into subfolders...** ‒ a set of tools to separate downloaded files if need be:
  - **by type** ‒ sort by file type (checking file extension). You can separate files by `videos`/`images`/`flash (RN)` or by extension itself. Note that both `jpeg` and `jpg` files will be placed into **jpg** folder
  - **by size** ‒ sort by file size (you'll have to provide a threshold, in Megabytes). You can use multiple thesholds, separated by space, in any order: `0.5 10 3.0 5.00`
  - **by score** ‒ sort by post score. Make sure that selected files include score in their names or this won't work. You can use multiple thesholds, separated by space, in any order: `100 250 50 500`
- **Help -> Tags** ‒ a quick list of tag types and how to use them (for selected module)
- **Tags checking** ‒ there is a small button near the **Tags** field. When pressed, Ruxx will try to quickly check if this search yields any results, so this won't work with tags which cannot be passed to website's search engine directly (`AND` group, `OR` groups with meta tags, etc.). As a result the **Tags** field will briefly flash green / red. Additionally, if successful, a window will appear showing the number of results found. Note that this number my be not equal to the files count you'll get downloaded, as date filters, file type filters and related posts filter do not apply during this quick check; when using `favorited_by:X` or `pool:X` special meta tags negative tags also do not apply (except for RN module `favorited_by` tag where it's supported natively)

### Tags syntax
Ruxx normally allows most symbols for tags search, there are some specifics though:  
1. Wildcards
- All modules support asterisk symbol `*` as wildcard in tags (any number of any symbols). You can use any number of wildcards in tags in any place: `b*m*e_cit*` instead of `baltimore_city`
  - Note that there is a bug in RX search engine which breaks frontal wildcards: `*_city` will work for RN and RS, but RX will return default result (all)
2. Meta tags
- Meta tags describe not the posted artwork but the post itself. RX, RN and RS all support meta tags
  - RX syntax: _name_**:**_value_ OR _name_**:=**_value_
  - RN syntax: _name_**=**_value_
  - RS syntax: _name_**:**_value_
- Some meta `-tags` can be used for exclusion: `-rating:explicit`
- Some meta tags support wildcards. Rules are very strict so this feature is yet to be enabled
- Some meta tags support inequality. These metatags can be used to set a range, ex. `id:>X id:<Y`. See below for more syntax
  - Meta `-tags` cannot be used with inequality, like `-score:<0`. Flip the comparison instead: `score:>=0`
  - Meta `-tags` cannot be used with sort: `-sort:score`, this syntax won't cause an error but its behavior is undefined. Please use common sense
- Although 'sorting' meta tags are fully supported (`sort` and `order` for RX / RS and RN respectively), you can only use them if they don't conflict with other parameters (ex. date filters)
- RX meta tags:
  - **id**: `id:X` (OR `id:=X`), `id:>X`, `id:<Y`, `id:>=X`, `id:<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score:X` (OR `score:=X`), `score:>X`, `score:<Y`, `score:>=X`, `score:<=Y`. `X`,`Y` = `<number>`
  - Rarely used ones:
    - parent: `parent:X` (OR `parent:=X`). `X` = `<post ID>`
    - width: `width:X` (OR `width:=X`), `width:>X`, `width:<Y`, `width:>=X`, `width:<=Y`. `X`,`Y` = `<number>`
    - height: `height:X` (OR `height:=X`), `height:>X`, `height:<Y`, `height:>=X`, `height:<=Y`. `X`,`Y` = `<number>`
    - user: `user:X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating name>`, ex. `safe`, `questionable`, `explicit`.
    - md5: `md5:X`, `X` = `<MD5 hash>`
    - source:
    - updated:
    - sort: `sort:X[:Y]`. `X` = `<sort type>`, ex. `score`, `id` (default). `Y` = `<sort direction>` (optional), `asc` or `desc` (default)
- RN meta tags:
  - **id**: `id=X`, `id>X`, `id<Y`, `id>=X`, `id<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score=X`, `score>X`, `score<Y`, `score>=X`, `score<=Y`. `X`,`Y` = `<number>`
  - **favorited_by**: `favorited_by=X`. `X` = `<user name>`
  - Rarely used ones:
    - width: `width=X`, `width>X`, `width<Y`, `width>=X`, `width<=Y`. `X`,`Y` = `<number>`
    - height: `height=X`, `height>X`, `height<Y`, `height>=X`, `height<=Y`. `X`,`Y` = `<number>`
    - user: `user=X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating letter>`, ex. `q`, `s`, etc.
    - order: `order=X`. `X` = `<sort type>`, `id_desc` or `score_desc`
- RS meta tags:
  - **id**: `id:X` (OR `id:=X`), `id:>X`, `id:<Y`, `id:>=X`, `id:<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score:X` (OR `score:=X`), `score:>X`, `score:<Y`, `score:>=X`, `score:<=Y`. `X`,`Y` = `<number>`
  - Rarely used ones:
    - width: `width:X` (OR `width:=X`), `width:>X`, `width:<Y`, `width:>=X`, `width:<=Y`. `X`,`Y` = `<number>`
    - height: `height:X` (OR `height:=X`), `height:>X`, `height:<Y`, `height:>=X`, `height:<=Y`. `X`,`Y` = `<number>`
    - user: `user:X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating name>`, ex. `safe`, `questionable`, `explicit`.
    - sort: `sort:X[:Y]`. `X` = `<sort type>`, ex. `score`, `id` (default). `Y` = `<sort direction>` (optional), `asc` or `desc` (default)
3. `OR` groups
- Ruxx syntax for `OR` group is simplified compared to what you would normally use for RX: `(tag1~tag2~...~tagN)` instead of `( tag1 ~ tag2 ~ ... ~ tagN )`
- Ruxx allows using `OR` groups for all modules, not just RX
- The syntax is also the same for all modules, don't use curvy brackets for RS
- `OR` group can't be negative and needs to be unwrapped:
  - `-(tag1~tag2~tag3)` => `-tag1 -tag2 -tag3`
- Since using meta tags in `OR` groups `(id:=X~score:=Y)` is broken (RX) or straight impossible (RS, RN), Ruxx will always unwrap such groups to process them properly
4. Negative groups
- Syntax: `-(tag1,tag2,...,tagN)`. Ruxx allows to filter out tag combinations (posts where all tags in group are present), which you can't normally do using website search engine. In addition to normal tag symbols, in negative group tags you can use wildcard symbols `?` and `*` for `any symbol` and `any number of any symbols` repectively. You can also use pipe symbol `|` for direct regex `OR` group composition. Example: `-(tag?1,ta*g2|tag3)` will be effectively converted to regular expressions `"^tag.1$"` and `"^ta.*g2|tag3$"` to check for, posts with tags matching both will get filtered out
    - Important note: unlike normal `-tags`, negative group will not check tag aliases
5. Tag limits
- Any valid search query requires at least one positive non-sorting tag to search for. Search query cannot be formed using just `sort:...` tag or `-tags` only
- Very long search queries will cause website to return empty result. Generally this happens when trying to add too many `-tags` to narrow down the search. If resulting query is too long Ruxx will automatically create a specific [negative group](#tags-syntax) from excessive `-tags` and use them as additional filter. The message will be given as follows: `<X> 'excluded tags combination' custom filter(s) parsed`

#### User credentials
Ruxx doesn't provide a method of authentication natively on either of supported sites. To use your identity during search you need to follow 3 simple steps:
- Log in normally using web browser
- Open `Web Developer tools -> Network` and reload the page, look for `request headers`
- Open `Headers / Cookies` window `<F3>` and fill the tables accordingly:
  - Headers: `User-Agent` (remove existing value first)
  - Cookies:
    - RX: `cf_clearance`, `user_id`, `pass_hash`
    - RN: `cf_clearance`, `shm_user`, `shm_session`
    - RS: `user_id`, `pass_hash`
  - Notes:
    - RN `cf_clearance` cookie duration is **15 minutes**
    
#### Favorites
Downloading user's favorites using native tags search functionality is only available with RN (see RN meta tags above), other websites don't implement that neither through tags nor through API  
In order to enable users to download one's favorites Ruxx implements `favorited_by` tag for other modules as well. It's an extra layer of functionality but here is what you need to use it:
- Syntax: `favorited_by:X`. `X` = `<user ID>`. User ID you can get from user's favorites page, it's a part of its web address. Note: this syntax is not invalid as RN tag either but it won't do anything there
- Downloading from RX favorites pages requires `cf_clearance` cookie (see above) as it isn't a part of dapi
- While searching favorites you can use normal filtering as well. Date filter, additional required / excluded tags, etc.
- Downloading favorites isn't particulary fast, Ruxx will need to fetch info for every item in the list in order to enable filtering
    
#### Pools
Downloading post pool using native tags search functionality is not possible and only RX implements pool functionality  
To download RX pool use special `pool` tag:
- Syntax: `pool:X`. `X` = `<pool ID>`. Pool ID you can get from pool page, it's a part of its web address.
- Downloading RX pool pages requires `cf_clearance` cookie (see above) as it isn't a part of dapi
- Pool posts can be filtered as well. Date filter, additional required / excluded tags, etc.
- Same as favorites, downloading using custom tags isn't particulary fast, Ruxx will need to fetch info for every item in the list in order to enable filtering

#### Using from console
- It is possible to use Ruxx as a cmdline tool. In main window you will find `Cmd` section ‒ it generates your cmdline arguments every time you make a change ‒ use those arguments as an example. In console window you may need to escape some of them (path, `OR` groups, tags containing dots, etc.). Most arguments are optional though ‒ the only ones required are `tags` (default module is RX)  
- Python 3.7 or greater required. See `requirements.txt` for additional dependencies. Install with:
  - `python -m pip install -r requirements.txt`

- To run Ruxx directly using python target `ruxx_cmd.py` or `ruxx_gui.py`
  - `python ruxx_cmd.py <...args>` - run Ruxx command
  - `python ruxx_gui.py` - run Ruxx GUI

Invoke `Ruxx --help` or `python ruxx_cmd.py --help` for full help

#### Logging
Ruxx will log most of its actions, which you can see in **Log** window  
If any problem occurs it will yield some info unless it's an unexpected fatal error. Ruxx is able to resolve most non-fatal networking errors and IO mishaps, including dropped searches (search overload), non-matching e-tags, file size mismatch, malformed packets, etc.
- **W1**: a minor problem, more of the info
- **W2**: a problem which is going to be fixed, but there is no guarantee it won't occur again
- **W3**: a rather serious problem, Ruxx will attempt to fix it, but it may be not enough, may lead to an error down the road
- **ERROR**: if you see this the download process may fail, Ruxx can only retry the failed action, in most cases that's enough

### Technical info
Ruxx is written in Python (3.7). Lines of code: 9100+. Executables built using PyInstaller (5.8 for Windows, 3.6 for Linux)

### Support
For bug reports, questions and feature requests use our [issue tracker](https://github.com/trickerer01/Ruxx/issues)
