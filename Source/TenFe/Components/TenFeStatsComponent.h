#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TenFeStatsComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FTenFeStatChanged, float, CurrentValue, float, MaximumValue);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FTenFeDeath);

UCLASS(ClassGroup=(TenFe), meta=(BlueprintSpawnableComponent))
class TENFE_API UTenFeStatsComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTenFeStatsComponent();

    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Stats")
    float ApplyDamage(float RawDamage, float Defense);

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Stats")
    bool ConsumeStamina(float Amount);

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Stats")
    void RestoreToFull();

    UFUNCTION(BlueprintPure, Category="Ten Fe|Stats")
    float GetHealthPercent() const;

    UFUNCTION(BlueprintPure, Category="Ten Fe|Stats")
    float GetStaminaPercent() const;

    UFUNCTION(BlueprintPure, Category="Ten Fe|Stats")
    bool IsDead() const { return CurrentHealth <= 0.0f; }

    UPROPERTY(BlueprintAssignable, Category="Ten Fe|Stats")
    FTenFeStatChanged OnHealthChanged;

    UPROPERTY(BlueprintAssignable, Category="Ten Fe|Stats")
    FTenFeStatChanged OnStaminaChanged;

    UPROPERTY(BlueprintAssignable, Category="Ten Fe|Stats")
    FTenFeDeath OnDeath;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Ten Fe|Stats", meta=(ClampMin="1.0"))
    float MaxHealth = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Ten Fe|Stats", meta=(ClampMin="1.0"))
    float MaxStamina = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Ten Fe|Stats", meta=(ClampMin="0.0"))
    float StaminaRegenerationPerSecond = 22.0f;

    UPROPERTY(BlueprintReadOnly, Category="Ten Fe|Stats")
    float CurrentHealth = 100.0f;

    UPROPERTY(BlueprintReadOnly, Category="Ten Fe|Stats")
    float CurrentStamina = 100.0f;

private:
    float SecondsSinceStaminaUse = 0.0f;
    float StaminaRegenerationDelay = 0.8f;
};
