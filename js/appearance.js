import { app } from "/scripts/app.js";

// NCE Utils 统一紫色主题
const NCE_THEME = {
    color: "#4a3b5c",      // 深紫色 (标题栏)
    bgcolor: "#6b5b7f",    // 中紫色 (节点背景)
    groupcolor: "#8b7ba8"  // 亮紫色 (分组)
};

app.registerExtension({
    name: "nce.utils.appearance",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        // 只处理 NCE 分类的节点
        if (!nodeData?.category?.startsWith("🐍 NCE")) return;

        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            onNodeCreated?.apply(this, arguments);

            // 应用统一的紫色主题
            this.color = NCE_THEME.color;
            this.bgcolor = NCE_THEME.bgcolor;
            if (this.groupcolor !== undefined) {
                this.groupcolor = NCE_THEME.groupcolor;
            }

            // 为浮点数节点设置精度
            if (nodeData?.name === "NCEFloatConstant" && this.widgets) {
                for (let widget of this.widgets) {
                    if (widget.type === "number" && widget.name === "value") {
                        widget.options = widget.options || {};
                        widget.options.precision = 2;
                    }
                }
            }
        };
    },
});
