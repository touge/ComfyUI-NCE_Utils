import { app } from "/scripts/app.js";
import { api } from "/scripts/api.js";

function imageDataToUrl(data) {
    if (!data || !data.filename) return "";
    return api.apiURL(
        `/view?filename=${encodeURIComponent(data.filename)}&type=${encodeURIComponent(data.type || "temp")}&subfolder=${encodeURIComponent(data.subfolder || "")}${app.getPreviewFormatParam()}${app.getRandParam()}`
    );
}

app.registerExtension({
    name: "nce.utils.image_comparer",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData?.name === "NCEImageComparer") {
            nodeType.prototype.onMouseEnter = function (e) {
                this.isPointerOver = true;
            };

            nodeType.prototype.onMouseLeave = function (e) {
                this.isPointerOver = false;
            };

            nodeType.prototype.onMouseMove = function (e, pos) {
                if (pos) {
                    this.pointerOverPos = [...pos];
                }
            };

            const onNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                const r = onNodeCreated?.apply(this, arguments);

                this.isPointerOver = false;
                this.pointerOverPos = [0, 0];
                this.compareImgs = []; // 使用 compareImgs 命名，避免被 ComfyUI V2 的 useImagePreviewWidget 误抓取未加载的 node.imgs 导致 60fps drawImage 异常死锁

                const widget = {
                    type: "custom",
                    name: "nce_comparer",
                    node: this,
                    selected: [],
                    _value: { images: [] },

                    set value(v) {
                        let cleanedVal = v.images || [];
                        let selected = cleanedVal.filter((d) => d.selected);
                        if (!selected.length && cleanedVal.length) {
                            cleanedVal[0].selected = true;
                        }
                        selected = cleanedVal.filter((d) => d.selected);
                        if (selected.length === 1 && cleanedVal.length > 1) {
                            const other = cleanedVal.find((d) => !d.selected);
                            if (other) other.selected = true;
                        }
                        this._value.images = cleanedVal;
                        selected = cleanedVal.filter((d) => d.selected);
                        this.setSelected(selected);
                    },

                    get value() {
                        return this._value;
                    },

                    setSelected(selected) {
                        this._value.images.forEach((d) => (d.selected = false));
                        this.node.compareImgs = [];
                        
                        for (const sel of selected) {
                            sel.selected = true;
                            if (!sel.loadedImg && sel.url) {
                                const img = new Image();
                                img.onload = () => {
                                    if (img.naturalWidth > 0 && img.naturalHeight > 0) {
                                        sel.loadedImg = img;
                                        this.node.compareImgs.push(img);
                                        const aspect = img.naturalWidth / img.naturalHeight;
                                        const nodeW = this.node.size[0] || 300;
                                        const targetH = nodeW / aspect + 50;
                                        if (this.node.size[1] < targetH) {
                                            this.node.setSize([nodeW, targetH]);
                                        }
                                        this.node.setDirtyCanvas(true, false);
                                    }
                                };
                                img.onerror = () => {
                                    console.warn("[NCE ImageComparer] 图像加载失败:", sel.url);
                                };
                                img.src = sel.url;
                            } else if (sel.loadedImg) {
                                this.node.compareImgs.push(sel.loadedImg);
                            }
                        }
                        this.selected = selected;
                    },

                    draw(ctx, node, width, y) {
                        if (!this.selected || !this.selected.length) return;

                        // 绘制底图 A
                        if (this.selected[0]) {
                            this.drawImage(ctx, this.selected[0], y);
                        }

                        // 鼠标 Hover 时绘制顶层图 B
                        if (this.selected[1] && node.isPointerOver && node.pointerOverPos) {
                            this.drawImage(ctx, this.selected[1], y, node.pointerOverPos[0]);
                        }
                    },

                    drawImage(ctx, imageItem, y, cropX) {
                        const img = imageItem?.loadedImg;
                        if (!img || !(img instanceof HTMLImageElement) || !img.complete || img.naturalWidth === 0 || img.naturalHeight === 0) {
                            return;
                        }

                        let [nodeWidth, nodeHeight] = this.node.size;
                        const imageAspect = img.naturalWidth / img.naturalHeight;
                        let height = nodeHeight - y;
                        if (height <= 0) return;

                        const widgetAspect = nodeWidth / height;
                        let targetWidth, targetHeight;
                        let offsetX = 0;

                        if (imageAspect > widgetAspect) {
                            targetWidth = nodeWidth;
                            targetHeight = nodeWidth / imageAspect;
                        } else {
                            targetHeight = height;
                            targetWidth = height * imageAspect;
                            offsetX = (nodeWidth - targetWidth) / 2;
                        }

                        const widthMultiplier = img.naturalWidth / targetWidth;
                        const sourceX = 0;
                        const sourceY = 0;
                        const sourceWidth = cropX != null ? (cropX - offsetX) * widthMultiplier : img.naturalWidth;
                        const sourceHeight = img.naturalHeight;
                        const destX = (nodeWidth - targetWidth) / 2;
                        const destY = y + (height - targetHeight) / 2;
                        const destWidth = cropX != null ? cropX - offsetX : targetWidth;
                        const destHeight = targetHeight;

                        ctx.save();
                        ctx.beginPath();
                        let globalCompositeOperation = ctx.globalCompositeOperation;

                        if (cropX != null) {
                            ctx.rect(destX, destY, destWidth, destHeight);
                            ctx.clip();
                        }

                        ctx.drawImage(img, sourceX, sourceY, sourceWidth, sourceHeight, destX, destY, destWidth, destHeight);

                        if (cropX != null && cropX >= (nodeWidth - targetWidth) / 2 && cropX <= targetWidth + offsetX) {
                            ctx.beginPath();
                            ctx.moveTo(cropX, destY);
                            ctx.lineTo(cropX, destY + destHeight);
                            ctx.globalCompositeOperation = "difference";
                            ctx.strokeStyle = "rgba(255, 255, 255, 1)";
                            ctx.lineWidth = 1;
                            ctx.stroke();
                        }

                        ctx.globalCompositeOperation = globalCompositeOperation;
                        ctx.restore();
                    },

                    computeSize(width) {
                        return [width, 20];
                    }
                };

                this.addCustomWidget(widget);
                this.comparerWidget = widget;

                return r;
            };

            const onExecuted = nodeType.prototype.onExecuted;
            nodeType.prototype.onExecuted = function (message) {
                onExecuted?.apply(this, arguments);

                const widget = this.comparerWidget;
                if (!widget) return;

                const a_images = message?.a_images || [];
                const b_images = message?.b_images || [];

                const imagesToChoose = [];
                for (const [i, d] of a_images.entries()) {
                    if (d) {
                        imagesToChoose.push({
                            name: a_images.length > 1 ? `A${i + 1}` : "A",
                            selected: i === 0,
                            url: imageDataToUrl(d),
                        });
                    }
                }
                for (const [i, d] of b_images.entries()) {
                    if (d) {
                        imagesToChoose.push({
                            name: b_images.length > 1 ? `B${i + 1}` : "B",
                            selected: i === 0,
                            url: imageDataToUrl(d),
                        });
                    }
                }

                widget.value = { images: imagesToChoose };
                this.setDirtyCanvas(true, false);
            };
        }
    },
});
