from src.RelationGraph.func.utils.config import dataset_path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset, DatasetDict

def save_data( df, use_augmentation=True, aug_times=1 ):

    # Step 1：数据预处理
    df = df[['职业类别', 'combined_text']].dropna()
    df.columns = ['label', 'text']

    # Step 2: 标签编码
    le = LabelEncoder()
    df['label_id'] = le.fit_transform(df['label'])

    # Step 3: 划分原始训练/验证/测试集
    train_df, temp_df = train_test_split(
        df, test_size=0.1, random_state=42, stratify=df['label_id']
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, random_state=42, stratify=temp_df['label_id']
    )

    # Step 4: 转换为 HuggingFace Dataset 并保存
    dataset = DatasetDict({
        'train': Dataset.from_pandas(train_df[['text', 'label_id']]),
        'validation': Dataset.from_pandas(val_df[['text', 'label_id']]),
        'test': Dataset.from_pandas(test_df[['text', 'label_id']])
    })

    dataset.save_to_disk(dataset_path)
