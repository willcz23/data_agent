SKU = T_amazon_settlement.sku

ID = T_amazon_product_cost.id

总销量（件）-total_sales = "T_amazon_settlement.type=Pedido
再会用T_amazon_settlement.quantity"

日均销量（件）= 总销量/30

净销量（件）= "总销量减去T_amazon_settlement.type=Reembolso的总数量
数量字段T_amazon_settlement.quantity"

净销售额（RMB）= "T_amazon_settlement.product_sales加上
T_amazon_settlementproduct_sales_tax"

售后损耗（RMB）= "业务规则cantidad [Reembolso] * (采购单价(RMB)+运费单价(RMB)+打包费0.8(RMB))
T_amazon_settlement.type=Reembolso判断这个耗损类型
T_amazon_settlement.quantity数量统计
T_amazon_product_cost.purchase_price_rmb 采购单价
T_amazon_product_cost.shipping_unit_price_rmb运费单价 
T_amazon_product_cost.packing_fee_rmb 打包费"

售后损耗率 = "售后损耗(RMB)/净销售额(RMB)"

"回款净所得=total*(汇损0.99)
总采购成本(RMB)=采购单价(RMB)*净销量
总运费(RMB)=运费单价(RMB)*净销量
打包费(RMB)=净销量*0.8
3%增值税(RMB)=净销售额*0.995*0.03  
毛利润=回款净所得-总采购成本(RMB)-总运费(RMB)-打包费(RMB)-售后损耗(RMB)-3%增值税(RMB）
回款净所得=T_amazon_settlement.total_amount 流水表的总净销售额*0.99
总采购成本(RMB)=T_amazon_product_cost.purchase_price_rmb*净销量
总运费(RMB)=T_amazon_product_cost.shipping_unit_price_rmb**净销量
打包费(RMB)=净销量*0.8
3%增值税(RMB)=净销售额*0.995*0.03  
毛利润=回款净所得-总采购成本(RMB)-总运费(RMB)-打包费(RMB)-售后损耗(RMB)-3%增值税(RMB）
"

毛利率 = "毛利润/净销售额"

广告费用（RMB）= "T_amazon_advertising.spend_mxn 计算总广告费，均摊到各个SKU 暂定"

广告费用占比 = 广告费(RMB)/含税净销售额(RMB)

仓储费（RMB）= "T_amazon_short_storage.estimated_monthly_storage_fee 总计
+T_amazon_long_storage.amount_charged   总计
两个总计相加"

仓储费占比 = "仓储费(RMB)/含税净销售额(RMB)"

测评费用（RMB）= "T_amazon_product_cost.evaluation_fee_rmb  测评费用根据SKU绑定"

测评占比 = "测评费(RMB)/含税净销售额(RMB)"

纯利润（RMB）= "毛利润(RMB)-广告费(RMB)-测评费（RMB）-仓储费(RMB)"

纯利率 = 纯利润/净销售额
