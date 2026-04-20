from RelationGraph.func.prepare.get_data import get_data_raw
from RelationGraph.func.prepare.init_data import init_data_raw
from RelationGraph.func.prepare.save_data_for_lora import save_data
from RelationGraph.func.train.lora.train import train_and_evaluate_lora

# Step 0：载入数据
df = get_data_raw()

# Step 1：处理数据
df = init_data_raw(df, if_lora = True)
save_data(df, use_augmentation = True)

# Step 2：调用模型
# train_and_evaluate_lora()


