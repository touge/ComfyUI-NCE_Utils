自用脚本，不提供技术支持。


20260803更新：

1. 融合 `Comfyui-Simple-Json-Node` 项目全部 10 个 JSON 处理节点，新增 `nodes/tools/json/` 目录进行集中管理（包含 JSON 解析器、生成器、合并、修改器、迭代器、格式化等节点）。
2. 配置 `NODE_CONFIG` 完成全部 JSON 节点的中文显示名称本地化映射，节点分类统一归入 `🐍 NCE/JSON`。
3. 优化 `NCEShowAnything`（显示任意类型）与 `NCEUtilsShowText`（展示文本）节点的长文本视图：为文本框增设自动滚动条（`overflow-y: auto`），限制最大高度防过度展开，并支持动态拖拽调宽高。


20260802更新：

1. 新增音频信息节点 `NCEGetAudioInfo`（获取音频信息），支持解析音频的时长（秒）、采样率（Hz）、通道数及总采样点数。
2. 重构音频节点目录，新建 `nodes/audios/` 目录，将音频信息节点与播放声音节点（`play_sound.py`）统一归集管理。


20250115更新：

1.新增本地化json语言文件。
如果安装过AIGODLIKE-COMFYUI-TRANSLATION插件，将translation/zh-CN/Nodes/ComfyUI-NCE_Utils.json，
拷贝到AIGODLIKE-COMFYUI-TRANSLATION/zh-CN/Nodes下，重启ComfyUI即可。

2.新增节点视频风格生成器
