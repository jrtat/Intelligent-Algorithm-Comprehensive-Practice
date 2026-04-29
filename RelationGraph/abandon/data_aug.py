class ModernLLMAug:
    def __init__(self, model_name="Qwen/Qwen2.5-7B-Instruct"):
        """
        使用你已有的 get_llm_silicon_flow 函数
        默认使用免费且效果优秀的 Qwen2.5-7B-Instruct
        """
        self.llm = get_llm_silicon_flow(model_name=model_name)
        print(f"LLM 增强器初始化完成（SiliconFlow API），使用模型: {model_name}")

    def _generate_paraphrases(self, text: str, num: int = 1):
        """调用 API 生成高质量同义句"""
        system_prompt = """你是一个专业的中文文本改写助手。
任务：为用户提供的句子生成{num}个**语义完全相同**、但**表达方式不同**的自然同义句。
要求：
1. 必须100%保留原意，不能添加或删除信息
2. 语言自然流畅，像母语者写的中文
3. 句子长度与原句接近
4. 每句占一行，不要编号，不要解释，直接输出句子"""

        user_prompt = f"""原句：{text}

请生成 {num} 个同义句："""

        messages = [
            SystemMessage(content=system_prompt.format(num=num)),
            HumanMessage(content=user_prompt)
        ]

        # 调用 API（覆盖低温度，增加多样性）
        response = self.llm.invoke(
            messages,
            temperature=0.85,      # 提高多样性
            top_p=0.9,
            max_tokens=512
        )

        # 解析输出
        content = response.content.strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]

        # 去重 + 过滤
        unique = []
        seen = set()
        for line in lines:
            if line != text and line not in seen and len(line) > 5:
                seen.add(line)
                unique.append(line)
                if len(unique) >= num:
                    break

        return unique

    def replace(self, sent: str, create_num: int = 1):
        """接口和原来 nlpcda.Simbert.replace 完全一致"""
        try:
            results = self._generate_paraphrases(sent, create_num)
            return results
        except Exception as e:
            print(f"LLM 增强失败: {e}")
            return []


# ====================== 使用函数（接口完全不变）======================
# 初始化（只需要执行一次）
simbert_aug = ModernLLMAug(
    model_name="Qwen/Qwen2.5-7B-Instruct"   # 免费且效果优秀，你也可以改成注释里的其他免费模型
)

def augment_with_simbert(text: str, generate_num: int = 1):
    """和原来完全一样的接口"""
    try:
        results = simbert_aug.replace(sent=text, create_num=generate_num)
        return [res for res in results if res and res != text]
    except Exception as e:
        print(f"LLM 增强失败: {e}")
        return []


def augment_texts_simbert(texts, labels, label_ids, aug_times=1):
    """批量增强函数（接口完全不变）"""
    new_texts, new_labels, new_label_ids = [], [], []

    for text, label, label_id in zip(texts, labels, label_ids):

        new_texts.append(text)
        new_labels.append(label)
        new_label_ids.append(label_id)

        generated_texts = augment_with_simbert(text, generate_num=aug_times)
        for gen_text in generated_texts:
            new_texts.append(gen_text)
            new_labels.append(label)
            new_label_ids.append(label_id)
            print(f"原句: {text}")
            print(f"修改后: {gen_text}")

    return pd.DataFrame({
        'text': new_texts,
        'label': new_labels,
        'label_id': new_label_ids
    })

def apply_augmentation_to_train(train_df, aug_times=1):
    """
    对训练集DataFrame应用指定的增强方法。

    :param train_df: 包含 text, label, label_id 的 DataFrame
    :param aug_times: 每条原始样本生成的新样本数
    :return: 增强后的训练集 DataFrame
    """
    texts = train_df['text'].tolist()
    labels = train_df['label'].tolist()
    label_ids = train_df['label_id'].tolist()

    combined_df = augment_texts_simbert(texts, labels, label_ids, aug_times)
    return combined_df

#--- 最终使用 ---#

if use_augmentation:
    print(f"正在进行训练集增强，每条原始样本生成 {aug_times} 条新样本...")
    train_df = apply_augmentation_to_train(train_df, aug_times=aug_times)
    print(f"增强后训练集大小：{len(train_df)}")