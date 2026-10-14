#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TenFeTrainingDummy.generated.h"

class UStaticMeshComponent;

UCLASS()
class TENFE_API ATenFeTrainingDummy : public AActor
{
    GENERATED_BODY()

public:
    ATenFeTrainingDummy();
    virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser) override;

private:
    void RestoreDummy();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> Mesh;

    float MaxHealth = 120.0f;
    float CurrentHealth = 120.0f;
};
