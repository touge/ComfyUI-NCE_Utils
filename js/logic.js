import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

function NCEShowAnythingNodeCreated(nodeType, nodeData) {
    const onNodeCreated = nodeType.prototype.onNodeCreated;

    // 定义 populate 函数
    function populate(text, source) {
        console.log(`NCEShowAnything - populate called from: ${source}`);
        console.log("NCEShowAnything - text:", text);
        console.log("NCEShowAnything - current widgets count:", this.widgets?.length || 0);

        // 防止重复调用
        if (this._isPopulating) {
            console.log("NCEShowAnything - SKIPPED: already populating");
            return;
        }
        this._isPopulating = true;

        // 清除所有旧的 widgets
        if (this.widgets) {
            for (let i = 0; i < this.widgets.length; i++) {
                this.widgets[i].onRemove?.();
            }
            this.widgets.length = 0;
        }

        // 处理 text 数据
        let v = [];
        if (Array.isArray(text)) {
            v = [...text];
        } else {
            v = [text];
        }

        // 移除空元素
        if (!v[0]) {
            v.shift();
        }

        console.log("NCEShowAnything - will create", v.length, "widgets");

        for (const list of v) {
            const w = ComfyWidgets["STRING"](this, "text", ["STRING", { multiline: true }], app).widget;
            w.inputEl.readOnly = true;
            w.inputEl.style.opacity = 0.6;
            w.value = list;
        }

        requestAnimationFrame(() => {
            const sz = this.computeSize();
            if (sz[0] < this.size[0]) {
                sz[0] = this.size[0];
            }
            if (sz[1] < this.size[1]) {
                sz[1] = this.size[1];
            }
            this.onResize?.(sz);
            app.graph.setDirtyCanvas(true, false);

            // 重置标志
            this._isPopulating = false;
        });
    }

    nodeType.prototype.onNodeCreated = function () {
        onNodeCreated?.apply(this, arguments);
    }

    // 事件处理器
    const onExecuted = nodeType.prototype.onExecuted;
    nodeType.prototype.onExecuted = function (message) {
        console.log("NCEShowAnything - onExecuted called");
        onExecuted?.apply(this, arguments);
        populate.call(this, message.text, "onExecuted");
    };

    const onConfigure = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
        console.log("NCEShowAnything - onConfigure called, widgets_values:", this.widgets_values);
        onConfigure?.apply(this, arguments);
        if (this.widgets_values?.length) {
            populate.call(this, this.widgets_values.slice(+this.widgets_values.length > 1), "onConfigure");
        }
    };
}

app.registerExtension({
    name: "nce.utils.logic",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (!nodeData?.category?.startsWith("🐍 NCE")) return;
        console.log(nodeData.name);
        switch (nodeData?.name) {
            case "NCEShowAnything":
                NCEShowAnythingNodeCreated(nodeType, nodeData);
                break;
        }
    },
});
