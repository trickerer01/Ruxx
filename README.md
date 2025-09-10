# Ruxx
[Download](https://github.com/trickerer01/Ruxx/releases/) [latest release](https://github.com/trickerer01/Ruxx/releases/latest/) (Windows, Linux)  
[![Downloads](https://img.shields.io/github/downloads/trickerer01/Ruxx/total?color=brightgreen&style=flat)](https://github.com/trickerer01/Ruxx/releases/)

### What the hell?
Ruxx is a content downloader with a lot of filters for maximum search precision (and ugly GUI). Supported websites are in description, everywhere else ‒ abbreviations only

### How to use
- \[Optional] Choose **Module** (website) to use. The icon in the bottom left corner will change accordingly
- Fill the **Tags** field with tags you want to search for. For base and quick advanced info on tags check **Help -> Tags** section. [More info](#tag-syntax)
- \[Optional] Configure **filters** to fine-tune your search. You can choose whether you want do download **videos**, **images** or **both**, add **post date** limits, number of **download threads**
- \[Optional] Choose the destination **Path**. Default path is current folder
- Press **Download**

![ruxx](https://github.com/user-attachments/assets/d5deb7c4-b942-4764-a78f-613d6a3df0af)

Note that Ruxx does not restrict your searches to a couple pages or something. You may even search for something like *id:>=0* (everything), this won't work though as websites actually put a limit on maximum search results returned. For something stupid like this you'll have to split your searches using id filter. Plus you may still get banned for abusing the resource. **Ruxx is not a scraping tool**

#### Download Options
- *Videos* ‒ some websites serve videos in multiple formats, here you can select a prefered one. You may also exclude videos altogether
- *Images* ‒ some websites serve images in multiple resolutions / quilities (full, preview), which you can choose from. Just like with the videos, you may also filter all the images out
- *Date min / max* ‒ applied to initial search results, format: `dd-mm-yyyy`, ignored if set to default (min: `01-01-1970`, max: `<today>`). Enter some gibberish to reset to default. RX, RN, RP, EN, XB and BB only
- *Parent posts / child posts* ‒ this switch allows to, in addition to initial search result, also download parent posts, all children and all found parents' children even if they don't match the tags you're searching for. RX, EN, XB and BB only
- *Threading* ‒ the number of download threads to use. This also somewhat increases the number of scan threads. More threads means speed, less threads means less network hiccups. Max threads is not a problem in most cases, but you must always remember that nobody likes reckless hammering of their services/APIs
- *Download order* - the order in which found posts will be downloaded. Default is ascending order (lowest id to highest id). Note that sort tags may alter the resulting download order
- *Posts limit* - the maximum number of posts to download. Default is `0` (no limit)

#### Misc & Tools
- **File -> Save settings...** \<Ctrl+S> ‒ allows you to save current run parameters to a config file for later or as a template. `Note that only recognized parameters will be loaded - missing parameters will just stay unchanged without any errors given, so if you want to not save some parameters (ex. window position) just remove associated rows from the file`
- **File -> Load settings...** \<Ctrl+O> ‒ load run parameters from previously saved config file. You can also put a `.cfg` file folder with executable and Ruxx will automatically pick it and configure itself. You have to use one of the following names: ['ruxx.cfg', 'auto.cfg', 'settings.cfg', 'config.cfg']
- **File -> Reset all settings** ‒ resets all settings to initial ones. If autoconfigured this will reset to those parameters. Window position is unaffected by this action
- **File -> Open download folder** \<Ctrl+L> ‒ open currently selected destination folder (**Path**), Windows only
- **View -> Log** ‒ open a log window, if you want some readable output
- **View -> Reveal module names** ‒ toggles between module abbreviation and website real name shown in module icon tooltip
- **Edit -> Prefix file names with \<prefix>** ‒ all downloaded file names will be prefixed according to selected module (`rx_`, `rn_`, etc.) so they are not just numbers. This option is enabled by default
- **Edit -> Save tags** ‒ an additional (text) file will be created containing tags for every post
- **Edit -> Save source links** ‒ an additional (text) file will be created containing source (if present) for every post
- **Edit -> Save comments** ‒ an additional (text) file will be created containing comments (if present) for every post
- **Edit -> Save info mode...** ‒ tags/sources/comments info file save mode
  - **per run** ‒ create a single file per checked info category for every (non-empty) downloader run, this is the default mode
  - **per file** ‒ create info files per each downloaded file (not recommended)
  - **merge info lists** ‒ gather and parse existing info files, merge and save all infos together, one text file per info category will be stored. **Parsed old info files will be deleted**
- **Edit -> Extend file names with extra info** ‒ all file names will include short representation of their major tags if any. This may extend resulting full path up to 240 symbols total
- **Edit -> Warn if download folder is not empty** ‒ in GUI mode you will be warned if destination folder is not empty and there is a potential risk of mixing up different search results
- **Edit -> Verbose log** ‒ Enable logging of technical messages not related to actual download process. Verbose log is one of the requirements for a proper issue report
- **Connection -> Headers / Cookies** \<F3> ‒ For some websites (RN) and in some other cases you'll have to provide your `cf_clearance` cookie, and the `User-Agent` header has to match the one used in your web browser for target website ‒ to find it while browsing said website open `Web Developer tools -> Network` (or similar), reload the page and check `request headers`
- **Connection -> Set proxy** \<F4> ‒ you can use proxy if you want or if target website is blocked in your country. SOCKS5 proxies are supported too
- **Connection -> Set timeout** \<F5> ‒ override connection timeout if need be
- **Connection -> Set retries count** \<F6> ‒ override connection retries count, may be useful when using a proxy
- **Connection -> API Key** \<F7> ‒ set API authentication info (RX only)
- **Connection -> Download without proxy** ‒ you can use this option if only the main domain of the selected module's website is blocked in your country
- **Connection -> Ignore proxy** ‒ this is just a switch that disables proxy temporarily without wiping it
- **Connection -> Cache processed HTML** ‒ by default HTML is cached as raw bytes, enabling this makes Ruxx cache HTML after it was processed into manageable form - a little bit faster but consumes much more memory. Mainly affects RS module
- **Actions -> Download** \<Ctrl+Shift+D> ‒ same as download button
- **Actions -> Check tags** \<Ctrl+Shift+C> ‒ same as check tags button
- **Actions -> Batch download using tag list...** ‒ read and process tags using a text file. Each line forms a string which then gets put into **Tags** field and downloaded. Warning: download starts immediately! Adjust settings and download options beforehand
- **Actions -> Clear log** \<Ctrl+Shift+E> ‒ same as clear log button
- **Tools -> Load from ID list** ‒ load **ID** tag list from a text file. The resulting tags will look like `(id:x~id:y~id:z)` which is an ***OR*** group [expression](#tag-syntax), effectively allowing you to search for those ids. ~~Broken since about 10.07.2021. Refer to "Broken things" RX forum subsection for details.~~ Re-enabled since version `1.1.284` for all modules using a workaround, but doesn't run in parallel so be aware of that
- **Tools -> Un-tag files...** ‒ renames selected Ruxx-downloaded media files, stripping file names of all extra info
- **Tools -> Re-tag files...** ‒ renames selected Ruxx-downloaded media files, re-appending extra info. You'll need dumped tags info file(s) (see **Edit -> Save tags**)
- **Tools -> Sort files into subfolders...** ‒ a set of tools used to separate downloaded files if need be:
  - **by type** ‒ sort by file type (checking file extension). You can separate files by `videos`/`images`/`flash (RN, EN)` or by extension itself. Note that both `jpeg` and `jpg` files will be placed into **jpg** folder
  - **by size** ‒ sort by file size (you'll have to provide a threshold, in Megabytes). You can use multiple thesholds, separated by space, in any order: `0.5 10 3.0 5.00`
  - **by score** ‒ sort by post score. Make sure that selected files include score in their names or this won't work. You can use multiple thesholds, separated by space, in any order: `100 250 50 500`
- **Tools -> Scan for duplicates...** ‒ download results deduplication tool. Select a folder and scan depth ‒ receive a list of binary equal files. Note that only media files will be scanned. Extra actions depend on selected option:
  - **and report** ‒ do nothing
  - **and separate** ‒ for each set of equal files leave one original file and **move** all its dupes to 'dupes' folder. The longest common path is used as base folder
  - **and remove** ‒ for each set of equal files leave one original file and **delete** all its dupes
- **Tools -> Enable autocompletion** ‒ this feature allows [tag autocompletion](#tag-autocompletion) within **Tags** field
- **Tools -> Autocomplete tag...** \<Ctrl+Space> ‒ trigger autocompletion at current cursor position. Note that the hotkey will only work when focusing the **Tags** field
- **Help -> Tags** ‒ a quick list of tag types and how to use them (for selected module)
- **Tags checking** ‒ there is a small button near the **Tags** field. When pressed, Ruxx will try to quickly check if this search yields any results, so this won't work with tags which cannot be passed to website's search engine directly (`AND` group, `OR` groups with meta tags, etc.). As a result the **Tags** field will briefly flash green / red. Additionally, if successful, a window will appear showing the number of results found. Note that this number my be not equal to the files count you'll get downloaded, as date filters, file type filters and related posts filter do not apply during this quick check; when using `favorited_by:X` or `pool:X` special meta tags negative tags also do not apply (except for RN module's `favorited_by` tag where it's supported natively)

### Tag syntax
Ruxx normally allows most symbols for tags search, there are some specifics though:  
1. Wildcards
- Most modules support asterisk symbol `*` as wildcard in tags (any number of any symbols). You can use any number of wildcards in tags in any place: `b*m*e_cit*` instead of `baltimore_city`.
  - Note that there is a bug in RX / XB / BB search engine which breaks frontal wildcards: `*_city` will work for RN, RS, RP and EN, but RX will return default result (all)
2. Meta tags
- Meta tags describe not the posted artwork but the post itself. RX, RN, RS, RP, EN, XB and BB all support meta tags:
  - RX syntax: _name_**:**_value_ OR _name_**:=**_value_
  - RN syntax: _name_**=**_value_
  - RS syntax: _name_**:**_value_
  - RP syntax: _name_**=**_value_
  - EN syntax: _name_**:**_value_
  - XB syntax: _name_**:**_value_ OR _name_**:=**_value_
  - BB syntax: _name_**:**_value_ OR _name_**:=**_value_
- Some meta `-tags` can be used for exclusion: `-rating:explicit`
- Some meta tags support wildcards. Rules are very strict so this feature is yet to be enabled
- Some meta tags support inequality. These metatags can be used to set a range, ex. `id:>X id:<Y`. See below for more syntax
  - Meta `-tags` cannot be used with inequality, like `-score:<0`. Flip the comparison instead: `score:>=0`
  - Meta `-tags` cannot be used with sort: `-sort:score`, this syntax won't cause an error but its behavior is undefined. Please use common sense
- Although 'sorting' meta tags are fully supported (`sort` and `order` for RX / RS / XB / BB and RN / RP respectively), you can only use them if they don't conflict with other parameters (ex. date filters)
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
- RP meta tags:
  - **id**: `id=X`, `id>X`, `id<Y`, `id>=X`, `id<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score=X`, `score>X`, `score<Y`, `score>=X`, `score<=Y`. `X`,`Y` = `<number>`
  - **favorited_by**: `favorited_by=X`. `X` = `<user name>`
  - Rarely used ones:
    - width: `width=X`, `width>X`, `width<Y`, `width>=X`, `width<=Y`. `X`,`Y` = `<number>`
    - height: `height=X`, `height>X`, `height<Y`, `height>=X`, `height<=Y`. `X`,`Y` = `<number>`
    - poster: `poster=X`. `X` = `<uploader name>`
    - order: `order=X`. `X` = `<sort type>`, `id_desc` or `score_desc`
- EN meta tags:
  - **id**: `id:X`, `id:>X`, `id:<Y`, `id:>=X`, `id:<=Y`. `X`,`Y` = `<post ID>`
  - **score**: `score:X`, `score:>X`, `score:<X`, `score:>=X`, `score:<=X`. `X`,`Y` = `<number>`.
  - **favorited_by**: `favorited_by:X`, `favoritedby:X` or `fav:X`. `X` = `<user name>`
  - Rarely used ones:
    - parent: `parent:X`. `X` = `<post ID>`
    - width: `width:X`, `width:>X`, `width:<Y`, `width:>=X`, `width:<=Y`. `X`,`Y` = `<number>`
    - height: `height:X`, `height:>X`, `height:<Y`, `height:>=X`, `height:<=Y`. `X`,`Y` = `<number>`
    - user: `user:X`. `X` = `<uploader name>`
    - rating: `rating:X`. `X` = `<rating name>`, ex. `safe`, `questionable`, `explicit`
    - md5: `md5:X`, `X` = `<MD5 hash>`
    - source:
    - updated:
    - sort: `sort:X[_asc|_desc]`. `X` = `<sort type>`, ex. `score`, `id` (default `id_desc`)
  - EN tags with range also support following range syntax:
    - `<type>:X..` (ex. `score:5000..` is equal to `score:>=5000`)
    - `<type>:..X` (ex. `score:..-500` <=> `score:<=-500`)
    - `<type>:X..` (ex. `id:5000000..` <=> `id:>=5000000`)
    - `<type>:X..Y` (ex. `score:90..99` <=> `score:>=90 score:<=99`)
- XB meta tags:
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
- BB meta tags:
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
3. `OR` groups
- Ruxx syntax for `OR` group is simplified compared to what you would normally use for RX: `(tag1~tag2~...~tagN)` instead of `( tag1 ~ tag2 ~ ... ~ tagN )`
- Ruxx allows using `OR` groups with any module, regardless of whether website supports it natively or not
- The syntax is also the same for all modules, don't use curvy brackets for RS
- `OR` group can't be negative and needs to be unwrapped:
  - `-(tag1~tag2~tag3)` => `-tag1 -tag2 -tag3`
- Since using meta tags in `OR` groups `(id:=X~score:=Y)` is broken (RX), not always reliable (EN) or straight impossible (RS, RN, RP), Ruxx will always unwrap such groups to process them properly
4. Negative groups
- Syntax: `-(tag1,tag2,...,tagN)`. Ruxx allows to filter out tag combinations (posts where all tags in group are present), which you can't normally do using website search engine. In addition to normal tag symbols, in negative group tags you can use wildcard symbols `?` and `*` for `any symbol` and `any number of any symbols` repectively. You can also use pipe symbol `|` for direct regex `OR` group composition. Example: `-(tag?1,ta*g2|tag3)` will be effectively converted to regular expressions `"^tag.1$"` and `"^ta.*g2|tag3$"` to check for, posts with tags matching both will get filtered out
    - Important note: unlike normal `-tags`, negative group will not check tag aliases
5. Tag limits
- Any valid search query requires at least one positive non-sorting tag to search for. Search query cannot be formed using just `sort:...` tag or `-tags` only
- Very long search queries will cause website to return empty result. Generally this happens when trying to add too many `-tags` to narrow down the search. If resulting query is too long Ruxx will automatically create a specific negative group from excessive `-tags` and use them as additional filter. The message will be given as follows: `<X> 'excluded tags combination' custom filter(s) parsed`
- Some websites also put a limit on the number of tags used. While most of the time this is a soft limit (web interface), sometimes they also apply a hard limit (api internals), namely:
  - `RP`: max `3` `tags & -tags`, `3` `total`
  - `EN`: max `40` `tags & -tags`, `40` `total`, max `1` `wildcard`
- In that case all extra `-tags` will be converted into a negative group and used locally as an internal filter (and mess up 'check tags' results). Note that this only applies to `-tags`, exceeding positive tag limit will result in an error
- It is recommended to manually convert all wildcarded `-t*ags` into a single negative group to prevent unwanted tag expansion (see below) resulting in too many `-tags`, it's simple really: `'-a -b -c -d* -f*g*h*j' -> '-a -b -c -(*,d*|f*g*h*j)'`
6. Tag validation
- All `tags`, `-tags` and `tags` in `OR` group have to be valid in order to get any search results. Tags are considered valid only if they:
  - have at least 10 posts tagged with them
  - do not contain any special symbols like `\r`,`\t`, etc., also `&` and unicode escaped sequences like `\u00a0`
- Wildcarded tags are expanded as follows:
  - `t*ags`: never (invalid)
  - `-t*ags`: always
  - `(t1~t*2)`: never (invalid)
  - `-(t1,t*2)`: never (converted to regex)
  - Log message example:
    ```shell script
    Expanding tags from wtag 'pale*s'...
     - 'pale_eyes'
     - 'pale_soles'
    ```
- To force a non-wildcarded tag without validation surround it with `%`, ex: `%mumbling%` (1 post, unlisted), or, if negative: `-%mumbling%`

#### Tag autocompletion
Ruxx provide lists of known tags for all modules, which can also be used to attempt to complete whatever word typed in **Tags** field
- Enable this feature by selecting **Tools -> Enable autocompletion**. You will be asked for a folder location - the folder containing tag list files. Once selected the following message will be logged (or similar):
  ```
  Found 7 tag lists:
   - <full path to folder>/rx_tags.json
   - <full path to folder>/rn_tags.json
   - <full path to folder>/rs_tags.json
   - <full path to folder>/rp_tags.json
   - <full path to folder>/en_tags.json
   - <full path to folder>/xb_tags.json
   - <full path to folder>/bb_tags.json
  ```
  Notes:
  - This can also be a parent folder if tag lists folder is default-named (`2tags/` or just `tags/`)
  - If tag lists exist inside current directory, or default-named tag lists folder inside current directory, tag lists will be found automatically
- Once autocompletion is enabled a new hotkey will become available `<Ctrl+Space>`, the first time you use it Ruxx will attempt to load current module tags into storage - this will require a little extra memory, that memory is also freed if autocompletion feature get disabled again
- If you prefer autocompletion to be enabled by default it is strongly recommended to save setting to *autoconfig* file

#### User credentials
Ruxx doesn't provide a method of authentication natively on either of supported sites. To use your identity during search you need to follow 3 simple steps:
- Log in normally using web browser
- Open `Web Developer tools -> Network` and reload the page, look for `request headers`
- Open `Headers / Cookies` window `<F3>` and fill Ruxx connection tables accordingly:
  - Headers: `User-Agent` (remove existing value first)
  - Cookies:
    - RX: `cf_clearance`, `user_id`, `pass_hash`
    - RN: `cf_clearance`, `shm_user`, `shm_session`
    - RS: `user_id`, `pass_hash`
    - RP: ?? (sign ups disabled)
    - EN: `_danbooru_session`, `remember`
    - XB: `cf_clearance`, `user_id`, `pass_hash`
  - Notes:
    - RN `cf_clearance` cookie duration is **15 minutes**

#### API authentication
Some modules (RX only actually) require authentication info provided in order to use their download API (dapi).  
It's strongly recommended to use your own API key and not rely on a default one. Visit module's respective website, sign in and generate yourself a key, you can then save it in config.

#### Favorites
Downloading user's favorites using native tags search functionality is only available with RN, RP and EN (see meta tags above), other websites don't implement that neither through tags nor through API. In order to enable users to download one's favorites Ruxx implements `favorited_by` tag for other modules as well. It's an extra layer of functionality but here is what you need to use it:
- Syntax: `favorited_by:X`. `X` = `<user ID>`. User ID you can get from user's favorites page, it's a part of its web address. Note: this syntax is not invalid as RN / RP / EN tag either but it won't do anything there
- Downloading from RX / XB / BB favorites pages requires `cf_clearance` cookie (see above) as it isn't a part of dapi
- While searching favorites you can use normal filtering as well. Date filter, additional required / excluded tags, etc.
- Downloading favorites isn't particulary fast, Ruxx will need to fetch info for every item in the list in order to enable filtering

#### Pools
Downloading post pool using native tags search functionality is not possible and only RX, EN, XB and BB implement pool functionality.  
To download a pool use special `pool` tag:
- Syntax: `pool:X`. `X` = `<pool ID>`. Pool ID you can get from pool page, it's a part of its web address
- EN module also supports pool name syntax: `pool:Y`. `Y` = `<pool name>`. Pool name must be in lower case and with all spaces replaced with underscores, ex. `'Long Night' -> 'pool:long_night'`
- Downloading RX / XB / BB pool pages requires `cf_clearance` cookie (see above) as it isn't a part of dapi
- Pool posts can be filtered as well. Date filter, additional required / excluded tags, etc.
- Same as favorites, downloading using custom tags isn't particulary fast (RX / XB / BB), Ruxx will need to fetch info for every item in the list in order to enable filtering

##### Sets
EN module also allows creating post sets. Essentially they are no different from pools:
- Syntax: `set:X`, `X` = `<set ID>`. Set ID can be extracted from set page address
- EN also supports set name syntax: `set:Y`. `Y` = `<set shortname>`. Important: set's short name isn't equal to its name in set list and is only listed on its own page!
- This is a native meta tag so:
  - posts can be filtered further if needed
  - download process suffers no speed penalty

#### Using from console
- It is possible to use Ruxx as a cmdline tool. In main window you will find `Cmd` section ‒ it generates your cmdline arguments every time you make a change ‒ use those arguments as an example. In console window you may need to escape some of them (path, `OR` groups, tags containing dots, etc.). Most arguments are optional though ‒ the only ones required are `tags` (default module is RX)  
- Python 3.9 or greater required. See `requirements.txt` for additional dependencies. Install with:
  - `python -m pip install -r requirements.txt`

- To run Ruxx directly using python target `ruxx_cmd.py` or `ruxx_gui.py`
  - `python ruxx_cmd.py <...args>` - run Ruxx command
  - `python ruxx_gui.py` - run Ruxx GUI
- ...or just use `ruxx.py` universally
  - `python ruxx.py <...args>` - run Ruxx command
  - `python ruxx.py <no args>` - run Ruxx GUI

Invoke `Ruxx --help` or `python ruxx_cmd.py --help` for full help

#### Logging
Ruxx will log most of its actions, which you can see in **Log** window  
If any problem occurs it will yield some info unless it's an unexpected fatal error. Ruxx is able to resolve most non-fatal networking errors and IO mishaps, including dropped searches (search overload), non-matching e-tags, file size mismatch, malformed packets, etc.
- **W1**: a minor problem, more of the info
- **W2**: a problem which is going to be fixed, but there is no guarantee it won't occur again
- **W3**: a rather serious problem, Ruxx will attempt to fix it, but it may be not enough, may lead to an error down the road
- **ERROR**: if you see this the download process may fail, Ruxx can only retry the failed action, in most cases that's enough

### Technical info
Ruxx is written in Python (3.9 for Windows, 3.11 for Linux). Lines of code: 13300+. Executables built using PyInstaller 6.1

### Support
For bug reports, questions and feature requests use our [issue tracker](https://github.com/trickerer01/Ruxx/issues)
