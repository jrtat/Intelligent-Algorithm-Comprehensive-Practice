from RelationGraph.func.use.use_lora_model import predict_probabilities


if __name__ == "__main__":
    result = predict_probabilities("具有5年Java后端开发经验，熟悉Spring Cloud微服务架构")
    # 按概率降序查看前5个最可能的职业
    top5 = sorted(result.items(), key=lambda x: x[1], reverse=True)[:5]
    for job, prob in top5:
        print(f"{job}: {prob:.4f}")