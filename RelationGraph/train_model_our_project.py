from RelationGraph.func.prepare.get_data import get_data_raw
from RelationGraph.func.prepare.init_data import init_data_raw
from RelationGraph.func.prepare.save_data_for_lora import save_data
from RelationGraph.func.model.lora.train_old import train_and_evaluate_lora
from RelationGraph.func.model.lora.evaluate import lora_predict_and_evaluate

# Step 0：载入数据
# df = get_data_raw()

# Step 1：处理数据（并存储）
# df = init_data_raw(df, if_lora = True)
# save_data(df, use_augmentation = True)

# Step 2：训练模型
train_and_evaluate_lora()

# Step 3：评价模型
lora_predict_and_evaluate(
    model_path="func/model/lora/model_ver1/lora_job_classifier",
    base_model_name="hfl/chinese-macbert-large",
    num_labels=51,                         # 请替换为实际类别数
    dataset_path="func/model/lora/dataset_raw/job_classify_dataset",  # 保存的数据集路径
    top_k_list=[1,2,3]
)