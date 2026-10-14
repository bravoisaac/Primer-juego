#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TenFeEquipmentMenuWidget.generated.h"

class ATenFeCharacter;
class UTextBlock;
class UVerticalBox;

UCLASS()
class TENFE_API UTenFeEquipmentMenuWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    void SetCharacter(ATenFeCharacter* InCharacter);

protected:
    virtual void NativeConstruct() override;
    virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
    void BuildLayout();
    void AddSectionLabel(UVerticalBox* Box, const FString& Label);
    void RefreshSummary();

    UFUNCTION() void SelectWeapon0();
    UFUNCTION() void SelectWeapon1();
    UFUNCTION() void SelectWeapon2();
    UFUNCTION() void EquipArmor0();
    UFUNCTION() void EquipArmor1();
    UFUNCTION() void EquipArmor2();
    UFUNCTION() void CloseMenu();

    UPROPERTY()
    TObjectPtr<ATenFeCharacter> Character;

    UPROPERTY()
    TObjectPtr<UTextBlock> SummaryText;
};
