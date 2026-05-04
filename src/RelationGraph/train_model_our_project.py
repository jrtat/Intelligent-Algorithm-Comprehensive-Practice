from src.RelationGraph.func.prepare.get_data import get_data_raw
from src.RelationGraph.func.prepare.init_data import init_data_raw
from src.RelationGraph.func.prepare.save_data_for_lora import save_data
from src.RelationGraph.func.model.lora.train_advance import train_and_evaluate_lora
from src.RelationGraph.func.model.lora.evaluate import lora_predict_and_evaluate
from src.RelationGraph.func.utils.config import model_path, dataset_path, model_name

# Step 0：载入数据
df = get_data_raw()

# Step 1：处理数据（并存储） 下面两行代码执行完一次就可以注释掉
df = init_data_raw(df, if_lora = True)
save_data(df, use_augmentation = False)


# Step 2：训练模型
train_and_evaluate_lora()

# Step 3：评价模型
lora_predict_and_evaluate(
    model_path=model_path,
    base_model_name=model_name,
    num_labels=51,
    dataset_path=dataset_path,  # 保存的数据集路径
    top_k_list=[1,2,3]
)
