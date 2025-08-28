SKU = T_mercado_sales_record.sku

ASNI/ID	= T_mercado_sales_record.publication_id

总销量（件）-total_sales = T_mercado_sales_record.units

日均销量（件）= 总销量/30

净销量（件）"判断 T_mercado_sales_record.cancellations_refunds<0
求退货总计 = sum(T_mercado_sales_record.units)
再拿总数据T_mercado_sales_record.units-退货总计"

净销售额（RMB）"判断总金额T_mercado_sales_record.total_amount>0 再计算
T_mercado_sales_record.product_revenue + T_mercado_sales_record.cancellations_refunds"

售后损耗（RMB）	"退货数量* (采购单价(RMB)+运费单价(RMB)+0.8(RMB))
退货数量根据前面计算，
采购单价 = T_mercado_product_cost.purchase_price_rmb
运费单价 = T_mercado_product_cost.shipping_unit_price_rmb"

售后损耗率 = 售后损耗(RMB)/净销售额(RMB)

毛利润（RMB）	"回款净所得=total*(汇损0.99)
总采购成本(RMB)=采购单价(RMB)*净销量
总运费(RMB)=运费单价(RMB)*净销量
打包费(RMB)=净销量*0.8
毛利润 = 回款净所得-总采购成本(RMB)-总运费(RMB)-打包费(RMB)-售后损耗(RMB)
判断总金额T_mercado_sales_record.total_amount>0
回款净所得=T_mercado_sales_record.total_amount>0 * 0.8
总采购成本(RMB)=T_mercado_product_cost.purchase_price_rmb * 净销量（件）
总运费(RMB)=T_mercado_product_cost.shipping_unit_price_rmb *净销量（件）
打包费(RMB)=净销量*0.8
毛利润=回款净所得-总采购成本(RMB)-总运费(RMB)-打包费(RMB)-售后损耗(RMB)"

毛利率 = 毛利润/净销售额

广告费用（RMB）	"通过publication_number 字段关联T_mercado_fee_advertisement.investment"

广告费用占比 = 广告费(RMB)/含税净销售额(RMB)

仓储费（RMB）"通过判断T_mercado_fee_summary.charge_detail 筛选值是不是这几个
Cargo por servicio de almacenamiento Full
Cargo por stock antiguo en Full
Cargo por retiro de stock Full  
金额数据字段：T_mercado_fee_summary.charge_amount  汇总总金额，按SKU数量来均摊费用。
通过SKU  ID来统计所有在库数量
T_mercado_inventory.sellable_units 为在库数量。"

仓储费占比 = 仓储费(RMB)/含税净销售额(RMB)

测评费用（RMB）	SKU 关联统计，T_mercado_product_cost.evaluation_fee_rmb

测评占比 = 测评费(RMB)/含税净销售额(RMB)

纯利润（RMB）= 毛利润(RMB)-广告费(RMB)-测评费（RMB）- 仓储费(RMB)

纯利率 = 纯利润/净销售额
