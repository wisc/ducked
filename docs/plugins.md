# Plugins

## Plugin types

There are three types of plugins:

- web search
- indexable scripts
- searchable scripts

## Web Search
Web search is located solely in the DB. Containing an icon, title and website to go to, which has the tag {query} injectable to hook into URL-based searches.

## Indexable scripts
Scripts that return JSON structured data, the same format as apps; icon, name, command. This will be indexed by the same, same as the installed apps.

The indexable scripts that are shipped with Ducked are in ducked/plugins/indexables/

## Searchable scripts
Scripts that can be searched through realtime. Setup in the DB similarly to Web Search.

The searchable scripts that are shipped with Ducked are in ducked/plugin/searchables/


## Making plugins

The output of a plugin (be it indexable or searchable) is in JSON, and should match the following:

```json
    [{
        "name": "Ducked",
        "icon": "/usr/share/local/icons/ducked-is-the-shit-yo-48x48.png",
        "command": "~/dothething.sh"
    }]
```

It's, of course, an array, and you can add as much results as you like.


### icon

The icon can either be the icon name (when the icon is placed in one of the regular icon dirs), or the full path. It should be 48x48.

### command

Full path to script. Can be any kind of script, as long as its executable.