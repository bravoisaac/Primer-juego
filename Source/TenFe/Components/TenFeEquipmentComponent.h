#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TenFeEquipmentComponent.generated.h"

UENUM(BlueprintType)
enum class ETenFeEquipmentSlot : uint8
{
    Weapon,
    Head,
    Chest,
    Legs
};

USTRUCT(BlueprintType)
struct FTenFeItemDefinition
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FName Id = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    FText DisplayName;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    ETenFeEquipmentSlot Slot = ETenFeEquipmentSlot::Weapon;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Damage = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Defense = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly)
    float Weight = 0.0f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FTenFeEquipmentChanged);

UCLASS(ClassGroup=(TenFe), meta=(BlueprintSpawnableComponent))
class TENFE_API UTenFeEquipmentComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UTenFeEquipmentComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Equipment")
    bool EquipWeapon(int32 Index);

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Equipment")
    bool EquipArmor(int32 Index);

    UFUNCTION(BlueprintCallable, Category="Ten Fe|Equipment")
    void CycleWeapon();

    UFUNCTION(BlueprintPure, Category="Ten Fe|Equipment")
    FTenFeItemDefinition GetEquippedWeapon() const;

    UFUNCTION(BlueprintPure, Category="Ten Fe|Equipment")
    float GetTotalDefense() const;

    UFUNCTION(BlueprintPure, Category="Ten Fe|Equipment")
    float GetEquipmentWeight() const;

    UPROPERTY(BlueprintReadOnly, Category="Ten Fe|Equipment")
    TArray<FTenFeItemDefinition> Weapons;

    UPROPERTY(BlueprintReadOnly, Category="Ten Fe|Equipment")
    TArray<FTenFeItemDefinition> Armors;

    UPROPERTY(BlueprintReadOnly, Category="Ten Fe|Equipment")
    int32 EquippedWeaponIndex = 0;

    UPROPERTY(BlueprintAssignable, Category="Ten Fe|Equipment")
    FTenFeEquipmentChanged OnEquipmentChanged;

private:
    void InitializeDefaultEquipment();
    int32 EquippedHeadIndex = INDEX_NONE;
    int32 EquippedChestIndex = INDEX_NONE;
    int32 EquippedLegsIndex = INDEX_NONE;
};
